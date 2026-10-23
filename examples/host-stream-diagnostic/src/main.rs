//! One real Linux stream consumer, not a Board driver or an exported SDK API.

#[cfg(not(target_os = "linux"))]
compile_error!("This diagnostic is qualified only for its Linux host experiment.");

use embedded_io::{ErrorKind, ErrorType, Read, ReadExactError, Write};
use std::io;
use std::net::Shutdown;
use std::os::unix::net::UnixStream;
use std::sync::mpsc::{self, Receiver, SyncSender};
use std::thread;
use std::time::{Duration, Instant};

const CONTROL_WAIT: Duration = Duration::from_secs(3);
const IO_WAIT: Duration = Duration::from_secs(1);
const SILENCE_WAIT: Duration = Duration::from_millis(100);
const REQUEST: [u8; 8] = *b"B01PING\n";
const RESPONSE: [u8; 8] = *b"B01PONG\n";

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Endpoint {
    Consumer,
    Peer,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Case {
    Response,
    Timeout,
    Cancel,
    PeerEof,
}

impl Case {
    fn name(self) -> &'static str {
        match self {
            Self::Response => "response",
            Self::Timeout => "timeout",
            Self::Cancel => "cancel",
            Self::PeerEof => "peer-eof",
        }
    }
}

#[derive(Debug)]
enum Event {
    Ready(Endpoint),
    RequestSeen([u8; 8]),
    PeerSent(&'static [u8]),
    Read {
        count: usize,
        micros: u128,
    },
    ReadError {
        raw: io::ErrorKind,
        upstream: ErrorKind,
        os: Option<i32>,
        micros: u128,
    },
    PeerEof,
    Closed(Endpoint),
}

fn notify(events: &SyncSender<Event>, event: Event) -> Result<(), String> {
    events
        .send(event)
        .map_err(|e| format!("control notification failed: {e}"))
}

/// A private adapter over actual blocking OS I/O. It adds no board semantics.
struct HostStream {
    socket: UnixStream,
    events: SyncSender<Event>,
}

impl ErrorType for HostStream {
    type Error = io::Error;
}

impl Read for HostStream {
    fn read(&mut self, buffer: &mut [u8]) -> io::Result<usize> {
        let start = Instant::now();
        let result = io::Read::read(&mut self.socket, buffer);
        let event = match &result {
            Ok(count) => Event::Read {
                count: *count,
                micros: start.elapsed().as_micros(),
            },
            Err(error) => Event::ReadError {
                raw: error.kind(),
                upstream: embedded_io::Error::kind(error),
                os: error.raw_os_error(),
                micros: start.elapsed().as_micros(),
            },
        };
        notify(&self.events, event).map_err(io::Error::other)?;
        result
    }
}

impl Write for HostStream {
    fn write(&mut self, buffer: &[u8]) -> io::Result<usize> {
        match io::Write::write(&mut self.socket, buffer) {
            Ok(0) if !buffer.is_empty() => Err(io::ErrorKind::WriteZero.into()),
            result => result,
        }
    }

    fn flush(&mut self) -> io::Result<()> {
        // UnixStream has no user-space write buffer. Peer receipt is checked
        // separately; this does not acknowledge device/peer completion.
        io::Write::flush(&mut self.socket)
    }
}

#[derive(Debug)]
enum ExchangeError<E> {
    Write(E),
    Flush(E),
    Read(ReadExactError<E>),
    UnexpectedResponse([u8; 8]),
}

/// The concrete non-Nostr consumer uses the upstream traits and their helpers.
/// Its only output is a complete, checked frame; errors return no partial frame.
fn exchange<S: Read + Write>(stream: &mut S) -> Result<[u8; 8], ExchangeError<S::Error>> {
    stream.write_all(&REQUEST).map_err(ExchangeError::Write)?;
    stream.flush().map_err(ExchangeError::Flush)?;
    let mut response = [0; 8];
    stream
        .read_exact(&mut response)
        .map_err(ExchangeError::Read)?;
    if response != RESPONSE {
        return Err(ExchangeError::UnexpectedResponse(response));
    }
    Ok(response)
}

type ConsumerResult = Result<Result<[u8; 8], ExchangeError<io::Error>>, String>;

fn consumer(mut stream: HostStream, start: Receiver<()>) -> ConsumerResult {
    let result = (|| {
        notify(&stream.events, Event::Ready(Endpoint::Consumer))?;
        start
            .recv_timeout(CONTROL_WAIT)
            .map_err(|e| format!("consumer start: {e}"))?;
        Ok(exchange(&mut stream))
    })();
    let close = stream.socket.shutdown(Shutdown::Both);
    let events = stream.events.clone();
    drop(stream);
    close.map_err(|e| format!("consumer shutdown: {e}"))?;
    notify(&events, Event::Closed(Endpoint::Consumer))?;
    result
}

fn peer(
    mut socket: UnixStream,
    start: Receiver<()>,
    events: SyncSender<Event>,
    case: Case,
) -> Result<(), String> {
    let result = (|| {
        notify(&events, Event::Ready(Endpoint::Peer))?;
        start
            .recv_timeout(CONTROL_WAIT)
            .map_err(|e| format!("peer start: {e}"))?;
        let mut request = [0; 8];
        io::Read::read_exact(&mut socket, &mut request)
            .map_err(|e| format!("peer request: {e}"))?;
        // The fixture oracle is literal and does not call consumer code.
        if request != *b"B01PING\n" {
            return Err(format!("peer rejected request: {request:02x?}"));
        }
        notify(&events, Event::RequestSeen(request))?;
        let bytes: &'static [u8] = match case {
            Case::Response => b"B01PONG\n",
            Case::Cancel | Case::PeerEof => b"B01",
            Case::Timeout => b"",
        };
        if !bytes.is_empty() {
            io::Write::write_all(&mut socket, bytes).map_err(|e| format!("peer response: {e}"))?;
            notify(&events, Event::PeerSent(bytes))?;
        }
        if case == Case::PeerEof {
            socket
                .shutdown(Shutdown::Write)
                .map_err(|e| format!("peer write-half shutdown: {e}"))?;
        }
        // Keeping the peer alive and reading makes premature close or an extra
        // request observable. In the timeout case it sends no bytes at all.
        let mut extra = [0; 1];
        let count = io::Read::read(&mut socket, &mut extra)
            .map_err(|e| format!("peer awaiting EOF: {e}"))?;
        if count != 0 {
            return Err(format!("peer received extra request byte: {extra:02x?}"));
        }
        notify(&events, Event::PeerEof)
    })();
    let close = socket.shutdown(Shutdown::Both);
    drop(socket);
    close.map_err(|e| format!("peer shutdown: {e}"))?;
    notify(&events, Event::Closed(Endpoint::Peer))?;
    result
}

fn configure(socket: &UnixStream, read_wait: Duration) -> Result<(), String> {
    socket
        .set_nonblocking(false)
        .map_err(|e| format!("blocking socket: {e}"))?;
    socket
        .set_read_timeout(Some(read_wait))
        .map_err(|e| format!("read timeout: {e}"))?;
    socket
        .set_write_timeout(Some(IO_WAIT))
        .map_err(|e| format!("write timeout: {e}"))?;
    let read = socket
        .read_timeout()
        .map_err(|e| format!("read back timeout: {e}"))?;
    let write = socket
        .write_timeout()
        .map_err(|e| format!("read back write timeout: {e}"))?;
    if read != Some(read_wait) || write != Some(IO_WAIT) {
        return Err(format!(
            "timeout configuration mismatch: read={read:?}, write={write:?}"
        ));
    }
    Ok(())
}

#[derive(Default)]
struct Observed {
    bytes_read: usize,
    read_zero: bool,
    read_errors: usize,
    request_seen: bool,
    peer_sent: usize,
    peer_eof: bool,
    cancelled: bool,
}

fn observe(
    events: Receiver<Event>,
    starts: [SyncSender<()>; 2],
    control: &UnixStream,
    case: Case,
) -> Result<Observed, String> {
    let mut ready = [false; 2];
    for _ in 0..2 {
        let event = events
            .recv_timeout(CONTROL_WAIT)
            .map_err(|e| format!("ready wait: {e}"))?;
        let Event::Ready(endpoint) = event else {
            return Err(format!("I/O before both ready: {event:?}"));
        };
        let index = usize::from(endpoint == Endpoint::Peer);
        if ready[index] {
            return Err(format!("duplicate ready: {endpoint:?}"));
        }
        ready[index] = true;
        println!("case={} phase=ready endpoint={endpoint:?}", case.name());
    }
    for start in starts {
        start.send(()).map_err(|e| format!("start gate: {e}"))?;
    }
    let mut observed = Observed::default();
    let mut closed = [false; 2];
    // Eight bytes limit successful read iterations to eight, plus one EOF/error.
    // This finite notification cap also prevents accidental unlimited control work.
    for _ in 0..20 {
        let event = events
            .recv_timeout(CONTROL_WAIT)
            .map_err(|e| format!("operation wait: {e}"))?;
        println!("case={} phase=io event={event:?}", case.name());
        match event {
            Event::RequestSeen(request) => {
                if observed.request_seen || request != *b"B01PING\n" {
                    return Err("invalid request observation".into());
                }
                observed.request_seen = true;
            }
            Event::PeerSent(bytes) => {
                let expected: &[u8] = match case {
                    Case::Response => b"B01PONG\n",
                    Case::Timeout => b"",
                    _ => b"B01",
                };
                if observed.peer_sent != 0 || bytes != expected {
                    return Err("invalid peer write observation".into());
                }
                observed.peer_sent = bytes.len();
            }
            Event::Read { count, micros } => {
                let _ = micros; // Retained as measured raw I/O time in the trace.
                observed.bytes_read += count;
                observed.read_zero |= count == 0;
                if observed.bytes_read > 8 {
                    return Err("response exceeded fixed buffer".into());
                }
                if case == Case::Cancel && !observed.cancelled {
                    if count == 0 || observed.bytes_read > 3 {
                        return Err("cancel prefix was not exactly B01".into());
                    }
                    if observed.bytes_read == 3 {
                        control
                            .shutdown(Shutdown::Both)
                            .map_err(|e| format!("cancel shutdown: {e}"))?;
                        observed.cancelled = true;
                        println!("case=cancel phase=shutdown-after-observed-prefix bytes=3");
                    }
                }
            }
            Event::ReadError {
                raw,
                upstream,
                os,
                micros,
            } => {
                observed.read_errors += 1;
                println!("case={} phase=read-error raw={raw:?} upstream={upstream:?} os={os:?} elapsed_us={micros}", case.name());
            }
            Event::PeerEof => {
                if observed.peer_eof {
                    return Err("duplicate peer EOF".into());
                }
                observed.peer_eof = true;
            }
            Event::Closed(endpoint) => {
                let index = usize::from(endpoint == Endpoint::Peer);
                if closed[index] {
                    return Err(format!("duplicate closure: {endpoint:?}"));
                }
                closed[index] = true;
            }
            Event::Ready(_) => return Err("ready repeated after start".into()),
        }
        if closed == [true, true] {
            return Ok(observed);
        }
    }
    Err("control notification limit exceeded".into())
}

fn run_case(case: Case) -> Result<(), String> {
    let start = Instant::now();
    let (client, server) = UnixStream::pair().map_err(|e| format!("socket pair: {e}"))?;
    let read_wait = if case == Case::Timeout {
        SILENCE_WAIT
    } else {
        IO_WAIT
    };
    configure(&client, read_wait)?;
    configure(&server, IO_WAIT)?;
    println!(
        "case={} phase=configured consumer_read_ms={} other_io_ms=1000 control_ms=3000",
        case.name(),
        read_wait.as_millis()
    );
    let client_control = client
        .try_clone()
        .map_err(|e| format!("client control clone: {e}"))?;
    let server_control = server
        .try_clone()
        .map_err(|e| format!("peer control clone: {e}"))?;
    let (events, receiver) = mpsc::sync_channel(32);
    let (client_start, client_gate) = mpsc::sync_channel(1);
    let (peer_start, peer_gate) = mpsc::sync_channel(1);
    let adapter = HostStream {
        socket: client,
        events: events.clone(),
    };
    let worker = thread::spawn(move || consumer(adapter, client_gate));
    let fixture = thread::spawn(move || peer(server, peer_gate, events, case));
    let observation = observe(receiver, [client_start, peer_start], &client_control, case);
    if let Err(error) = &observation {
        eprintln!(
            "case={} phase=failed-control error={error}; connections quarantined until collection",
            case.name()
        );
        // Still collect both workers; the external process watchdog handles an
        // OS/thread that cannot be collected. No partial buffer is returned.
        let client_close = client_control.shutdown(Shutdown::Both);
        let peer_close = server_control.shutdown(Shutdown::Both);
        eprintln!("cleanup client={client_close:?} peer={peer_close:?}");
    }
    drop(client_control);
    drop(server_control);
    println!("case={} phase=collecting", case.name());
    // Do both joins before inspecting either result: no failure detaches a peer.
    let worker_join = worker.join();
    let peer_join = fixture.join();
    println!(
        "case={} phase=joined consumer={} peer={}",
        case.name(),
        worker_join.is_ok(),
        peer_join.is_ok()
    );
    let observed = observation?;
    let response = worker_join.map_err(|_| "consumer thread panicked")??;
    peer_join.map_err(|_| "peer thread panicked")??;
    if !observed.request_seen || !observed.peer_eof {
        return Err("missing request or peer EOF".into());
    }
    match (case, response) {
        (Case::Response, Ok(bytes))
            if bytes == *b"B01PONG\n"
                && observed.bytes_read == 8
                && observed.peer_sent == 8
                && !observed.read_zero
                && observed.read_errors == 0 =>
        {
            println!("case=response phase=publish response_hex=423031504f4e470a");
        }
        (Case::Timeout, Err(ExchangeError::Read(ReadExactError::Other(error))))
            if error.kind() == io::ErrorKind::WouldBlock
                && error.kind() != io::ErrorKind::TimedOut
                && embedded_io::Error::kind(&error) == ErrorKind::Other
                && observed.bytes_read == 0
                && observed.peer_sent == 0
                && !observed.read_zero
                && observed.read_errors == 1 =>
        {
            println!(
                "case=timeout phase=rejected raw={:?} upstream={:?} os={:?} published=false",
                error.kind(),
                embedded_io::Error::kind(&error),
                error.raw_os_error()
            );
        }
        (Case::Cancel | Case::PeerEof, Err(ExchangeError::Read(ReadExactError::UnexpectedEof)))
            if observed.bytes_read == 3
                && observed.peer_sent == 3
                && observed.read_zero
                && observed.read_errors == 0
                && observed.cancelled == (case == Case::Cancel) =>
        {
            println!(
                "case={} phase=rejected error=UnexpectedEof published=false",
                case.name()
            );
        }
        (_, Err(ExchangeError::UnexpectedResponse(bytes))) => {
            return Err(format!("unexpected full response: {bytes:02x?}"))
        }
        (_, outcome) => return Err(format!("outcome violates frozen oracle: {outcome:?}")),
    }
    println!(
        "case={} result=PASS elapsed_us={} collected=true handles_closed=true",
        case.name(),
        start.elapsed().as_micros()
    );
    Ok(())
}

fn main() -> std::process::ExitCode {
    if std::env::args_os().len() != 1 {
        eprintln!("Usage: host-stream-diagnostic (runs all four frozen cases)");
        return std::process::ExitCode::FAILURE;
    }
    println!(
        "host-stream-diagnostic version={} linux_host_only=true request_hex=42303150494e470a",
        env!("CARGO_PKG_VERSION")
    );
    for case in [Case::Response, Case::Timeout, Case::Cancel, Case::PeerEof] {
        if let Err(error) = run_case(case) {
            eprintln!("case={} result=FAIL error={error}", case.name());
            return std::process::ExitCode::FAILURE;
        }
    }
    println!("result=PASS cases=4 board_support=false physical_evidence=false");
    std::process::ExitCode::SUCCESS
}
