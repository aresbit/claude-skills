# Concurrency — `Thread` and `Chan`

CII provides cooperative/preemptive **user-level threads** (`Thread`) that communicate through synchronous **channels** (`Chan`) — a CSP-style model where you share data by *communicating*, not by sharing memory.

Headers: `headers/{thread,chan}.h`.

## `Thread` — user-level threads

```c
const Except_T Thread_Failed;    /* thread machinery failed */
const Except_T Thread_Alerted;   /* this thread was alerted (see Thread_alert) */

int  Thread_init(int preempt, ...);   /* MUST be called once before any other Thread op */
T    Thread_new (int apply(void *), void *args, int nbytes, ...);
void Thread_exit(int code);           /* terminate current thread with exit code */
void Thread_alert(T t);               /* request t to raise Thread_Alerted */
T    Thread_self(void);
int  Thread_join(T t);                /* wait for t (or all threads if t==NULL) */
void Thread_pause(void);              /* yield to another runnable thread */
```

Usage rules:
- Call `Thread_init(preempt, ...)` exactly once at startup. `preempt != 0` requests preemptive scheduling (time-sliced); `0` is purely cooperative — threads run until they `Thread_pause`, block on a channel, or exit.
- `Thread_new(apply, args, nbytes, ...)` starts a thread running `apply(args)`. If `nbytes > 0`, CII **copies** `nbytes` from `args` into thread-private storage (so the args can be stack-local); pass `nbytes == 0` to share the pointer as-is.
- `Thread_join(t)` blocks until `t` finishes and returns its exit code; `Thread_join(NULL)` waits for all other threads. The thread function's `return` value is its exit code (same as `Thread_exit`).
- **Alerts** are the cancellation mechanism: `Thread_alert(t)` causes `t` to raise `Thread_Alerted` at its next blocking point, so a thread can be interrupted cleanly via the exception machinery — wrap interruptible sections in `TRY … EXCEPT(Thread_Alerted) …`.
- Raises `Thread_Failed` when the underlying mechanism (stack allocation, context switch) fails.

In cooperative mode you reason about a single logical flow with explicit yield points — no locks needed for code between yields. With `preempt`, treat shared mutable state as genuinely concurrent.

## `Chan` — synchronous channels

```c
T   Chan_new   (void);
int Chan_send  (T c, const void *ptr, int size);   /* blocks until a receiver takes it */
int Chan_receive(T c,      void *ptr, int size);    /* blocks until a sender provides it */
void  /* freed implicitly when last reference drops; no Chan_free in base interface */
```

A channel is **unbuffered and synchronous (rendezvous)**: `Chan_send` blocks until some thread calls `Chan_receive` on the same channel, and vice-versa. At the meeting point CII copies `min(send size, receive size)` bytes from the sender's `ptr` to the receiver's `ptr`; both calls return the number of bytes transferred. This copy-by-value handoff is what makes channels safe — ownership transfers with the data, no shared aliasing required.

### Idiom: producer/consumer

```c
int producer(void *cl) {
    Chan_T c = *(Chan_T *)cl;
    for (int i = 0; i < N; i++)
        Chan_send(c, &i, sizeof i);   /* each send waits for a receiver */
    return 0;
}
int consumer(void *cl) {
    Chan_T c = *(Chan_T *)cl;
    int v;
    while (Chan_receive(c, &v, sizeof v) > 0)
        use(v);
    return 0;
}

Thread_init(0);
Chan_T c = Chan_new();
Thread_new(producer, &c, sizeof c);
Thread_new(consumer, &c, sizeof c);
Thread_join(NULL);
```

## Model summary

- Threads = independent control flow; channels = the *only* sanctioned way they exchange data. Prefer passing values over channels to sharing mutable globals.
- Synchronous channels double as synchronization: a successful send/receive is a happens-before edge, so you rarely need explicit locks.
- Alerts + `Thread_Alerted` give structured cancellation through the exception system.

Implementation (a context-switch core in `swtch.s` / `thread.c`, plus `thread-nt.c` for Windows): docs ch20 (Thread) ch21 (Chan). The `sem.h` semaphore interface and `spin.c` are supporting examples.
