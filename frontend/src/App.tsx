import { useCallback, useEffect, useRef, useState } from "react";
import type { FormEvent, ReactNode } from "react";
import {
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  Check,
  ChevronRight,
  Film,
  Link2,
  LogOut,
  MessageCircle,
  Plus,
  Play,
  Search,
  Send,
  Settings2,
  Sparkles,
  X,
} from "lucide-react";
import { api, ApiError } from "./api";
import type { Conversation, Message, User, Video } from "./api";
import { Button, IconButton, OutlineButton } from "./material";
import { ThemeSelect } from "./theme";

const names = {
  youtube: "YouTube Shorts",
  instagram: "Instagram",
  tiktok: "TikTok",
};
const errorText = (error: unknown) =>
  error instanceof Error
    ? error.message
    : "Something went wrong. Please try again.";
const time = (value: string) =>
  new Date(value).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

function sharedLink() {
  const params = new URLSearchParams(window.location.search);
  if (window.location.pathname === "/share") {
    const value = [params.get("url"), params.get("text"), params.get("title")]
      .filter(Boolean)
      .join(" ");
    const url = value.match(/https:\/\/[^\s<>]+/)?.[0]?.replace(/[),.!]+$/, "");
    if (url) sessionStorage.setItem("vertical-share", url);
    window.history.replaceState({}, "", "/");
  }
  return sessionStorage.getItem("vertical-share") || "";
}

function Avatar({ user, small = false }: { user: User; small?: boolean }) {
  return (
    <span className={`avatar ${small ? "small" : ""}`} aria-hidden="true">
      {user.display_name.slice(0, 1).toUpperCase()}
    </span>
  );
}

function Logo() {
  return (
    <span className="brand">
      <span className="brand-mark">
        v<span>·</span>
      </span>
      vertical<span className="beta">BETA</span>
    </span>
  );
}
function ErrorNotice({ children }: { children: ReactNode }) {
  return (
    <div className="error" role="alert">
      {children}
    </div>
  );
}

function Modal({
  title,
  close,
  children,
}: {
  title: string;
  close: () => void;
  children: ReactNode;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    ref.current?.showModal();
  }, []);
  return (
    <dialog
      ref={ref}
      onCancel={close}
      onClick={(e) => {
        if (e.target === e.currentTarget) close();
      }}
    >
      <div className="modal-header">
        <h2>{title}</h2>
        <IconButton aria-label="Close dialog" onClick={close}>
          <X size={22} />
        </IconButton>
      </div>
      {children}
    </dialog>
  );
}

function Auth({
  signedIn,
  shared,
}: {
  signedIn: (user: User) => void;
  shared: string;
}) {
  const [register, setRegister] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    const values = Object.fromEntries(new FormData(event.currentTarget));
    setBusy(true);
    setError("");
    try {
      signedIn(
        (
          await api<{ user: User }>(
            `/auth/${register ? "register" : "login"}`,
            { method: "POST", body: JSON.stringify(values) },
          )
        ).user,
      );
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <main className="auth-shell">
      <section className="auth-story">
        <div className="auth-topbar">
          <Logo />
          <ThemeSelect />
        </div>
        <div className="story-content">
          <span className="eyebrow">
            <span className="live-dot" /> MADE TO BE SHARED
          </span>
          <h1>
            One more video.
            <br />
            <em>One closer friend.</em>
          </h1>
          <p>
            The rabbit hole is better together. Bring your favorite videos into
            a conversation that keeps going.
          </p>
          <div className="story-art" aria-hidden="true">
            <div className="art-orbit" />
            <div className="art-video">
              <span className="video-pill">THE GOOD STUFF</span>
              <div className="art-sun" />
              <div className="art-hill hill-one" />
              <div className="art-hill hill-two" />
              <span className="art-play">▶</span>
              <div className="art-caption">
                a little change
                <br />
                of perspective.
              </div>
            </div>
            <div className="art-chat">
              this is so us <span>↗</span>
            </div>
            <div className="art-chat secondary">You have to see this.</div>
          </div>
          <div className="platform-row">
            <span>TikTok</span>
            <span>Instagram Reels</span>
            <span>YouTube Shorts</span>
          </div>
        </div>
        <p className="story-footer">
          Less scrolling alone. More “thought of you.”
        </p>
      </section>
      <section className="auth-form-panel">
        <span className="edition">VERTICAL GENERATION MESSENGER / 01</span>
        <div className="auth-form-wrap">
          <div className="form-symbol">
            <MessageCircle size={26} />
          </div>
          <h2>{register ? "Find your people." : "Good to see you."}</h2>
          <p className="muted">
            {register
              ? "Make a little space for your favorite people."
              : "Your people. Your videos. All in one place."}
          </p>
          {shared && (
            <div className="share-notice">
              <Film size={20} /> Your shared video is saved. Sign in to choose a
              conversation.
            </div>
          )}
          <form onSubmit={submit}>
            {register && (
              <label>
                Display name
                <input
                  name="display_name"
                  autoComplete="name"
                  maxLength={60}
                  required
                  placeholder="What should we call you?"
                />
              </label>
            )}
            <label>
              Username
              <input
                name="username"
                autoComplete="username"
                pattern="[A-Za-z0-9_]{3,32}"
                minLength={3}
                maxLength={32}
                required
                placeholder="your_username"
              />
            </label>
            <label>
              Password
              <input
                name="password"
                type="password"
                autoComplete={register ? "new-password" : "current-password"}
                minLength={10}
                maxLength={128}
                required
                placeholder="At least 10 characters"
              />
            </label>
            {error && <ErrorNotice>{error}</ErrorNotice>}
            <Button type="submit" disabled={busy} className="auth-submit">
              {busy
                ? "Just a moment…"
                : register
                  ? "Create account"
                  : "Sign in"}
              <ArrowRight size={18} />
            </Button>
          </form>
          <p className="auth-switch">
            {register ? "Already in the loop?" : "New around here?"}{" "}
            <button
              onClick={() => {
                setRegister(!register);
                setError("");
              }}
            >
              {register ? "Sign in" : "Create an account"}
            </button>
          </p>
          <div className="auth-note">
            <Link2 size={18} />
            <span>Send a link. Watch it right in your chat.</span>
          </div>
        </div>
        <span className="edition bottom">
          A SMALLER FEED. A BETTER CONNECTION.
        </span>
      </section>
    </main>
  );
}

function Profile({
  user,
  close,
  update,
}: {
  user: User;
  close: () => void;
  update: (u: User) => void;
}) {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    try {
      update(
        (
          await api<{ user: User }>("/me", {
            method: "PATCH",
            body: JSON.stringify(
              Object.fromEntries(new FormData(e.currentTarget)),
            ),
          })
        ).user,
      );
      close();
    } catch (err) {
      setError(errorText(err));
    } finally {
      setBusy(false);
    }
  }
  return (
    <Modal title="Your profile" close={close}>
      <form onSubmit={submit}>
        <div className="profile-summary">
          <Avatar user={user} />
          <span>@{user.username}</span>
        </div>
        <label>
          Display name
          <input
            name="display_name"
            defaultValue={user.display_name}
            required
            maxLength={60}
          />
        </label>
        <label>
          A little about you
          <textarea
            name="bio"
            defaultValue={user.bio}
            maxLength={280}
            rows={3}
            placeholder="What’s catching your eye lately?"
          />
        </label>
        {error && <ErrorNotice>{error}</ErrorNotice>}
        <Button type="submit" disabled={busy}>
          {busy ? "Saving…" : "Save changes"}
        </Button>
      </form>
    </Modal>
  );
}

function NewChat({
  close,
  opened,
}: {
  close: () => void;
  opened: (c: Conversation) => void;
}) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [opening, setOpening] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    if (!query.trim()) {
      setResults([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    const timer = window.setTimeout(() => {
      api<{ users: User[] }>(`/users?q=${encodeURIComponent(query.trim())}`, {
        signal: controller.signal,
      })
        .then((data) => {
          setResults(data.users);
          setError("");
        })
        .catch((e) => {
          if (!controller.signal.aborted) setError(errorText(e));
        })
        .finally(() => {
          if (!controller.signal.aborted) setLoading(false);
        });
    }, 250);
    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [query]);
  async function start(user: User) {
    setOpening(true);
    try {
      opened(
        await api<Conversation>("/conversations", {
          method: "POST",
          body: JSON.stringify({ recipient_id: user.id }),
        }),
      );
      close();
    } catch (e) {
      setError(errorText(e));
    } finally {
      setOpening(false);
    }
  }
  return (
    <Modal title="Start a conversation" close={close}>
      <p className="muted">Find someone by their username or display name.</p>
      <label className="search-field">
        <Search size={19} />
        <input
          aria-label="Search people"
          autoFocus
          maxLength={60}
          placeholder="Find your people…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </label>
      {error && <ErrorNotice>{error}</ErrorNotice>}
      <div className="search-results" aria-live="polite">
        {loading ? (
          <p className="muted">Looking for your people…</p>
        ) : (
          results.map((user) => (
            <button
              className="person-row"
              key={user.id}
              disabled={opening}
              onClick={() => start(user)}
            >
              <Avatar user={user} />
              <span>
                <strong>{user.display_name}</strong>
                <small>@{user.username}</small>
              </span>
              <ChevronRight size={20} />
            </button>
          ))
        )}
        {!loading && !results.length && (
          <p className="muted">
            {query.trim()
              ? "No people found. Try another name."
              : "A good conversation starts with a hello."}
          </p>
        )}
      </div>
    </Modal>
  );
}

function VideoPlayer({ video }: { video: Video }) {
  const [started, setStarted] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [slow, setSlow] = useState(false);
  const [failed, setFailed] = useState(false);
  const frame = useRef<HTMLIFrameElement>(null);
  useEffect(() => {
    if (!started || loaded) return;
    const timer = window.setTimeout(() => setSlow(true), 10000);
    return () => window.clearTimeout(timer);
  }, [started, loaded]);
  useEffect(() => {
    function playerMessage(event: MessageEvent) {
      if (
        event.origin !== "https://www.tiktok.com" ||
        event.source !== frame.current?.contentWindow
      )
        return;
      if (event.data?.type === "onPlayerError") setFailed(true);
    }
    window.addEventListener("message", playerMessage);
    return () => window.removeEventListener("message", playerMessage);
  }, []);
  return (
    <div className={`video-message ${video.platform}`}>
      <div className="video-source">
        <Film size={14} />
        <span>{names[video.platform]}</span>
        <span className="source-dot" />
      </div>
      <div className="player-frame">
        {started ? (
          <>
            <iframe
              ref={frame}
              src={video.embed_url}
              title={`${names[video.platform]} video`}
              onLoad={() => setLoaded(true)}
              onError={() => setFailed(true)}
              allow="autoplay; encrypted-media; fullscreen; picture-in-picture; web-share"
              allowFullScreen
              referrerPolicy="strict-origin-when-cross-origin"
            />
            {(!loaded || failed) && (
              <div className="player-status" role="status">
                <Film size={24} />
                <p>
                  {failed
                    ? "The platform could not play this video."
                    : slow
                      ? "The platform is taking longer than usual."
                      : "Loading your video…"}
                </p>
                {(slow || failed) && (
                  <button
                    onClick={() => {
                      setStarted(false);
                      setLoaded(false);
                      setSlow(false);
                      setFailed(false);
                    }}
                  >
                    Try again
                  </button>
                )}
              </div>
            )}
          </>
        ) : (
          <button
            className="player-cover"
            onClick={() => setStarted(true)}
            aria-label={`Play ${names[video.platform]} video`}
          >
            <span className="cover-orbit" />
            <span className="cover-play">
              <Play size={28} fill="currentColor" />
            </span>
            <strong>
              Something worth
              <br />
              sharing.
            </strong>
            <span>
              Play {names[video.platform]} <ArrowRight size={14} />
            </span>
          </button>
        )}
      </div>
      <details className="video-help">
        <summary>Video not playing?</summary>
        <p>
          Private, removed, or restricted videos may not play here. The platform
          may require sign-in.
        </p>
        <a href={video.canonical_url} target="_blank" rel="noreferrer">
          Open on {names[video.platform]} ↗
        </a>
      </details>
    </div>
  );
}

function Composer({
  conversationId,
  shared,
  sharedSent,
  sent,
}: {
  conversationId: string;
  shared: string;
  sharedSent: () => void;
  sent: (m: Message) => void;
}) {
  const [text, setText] = useState("");
  const [url, setUrl] = useState(shared);
  const [videoMode, setVideoMode] = useState(!!shared);
  const [preview, setPreview] = useState<Video | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const pending = useRef<{ content: string; id: string } | null>(null);
  useEffect(() => {
    setPreview(null);
    if (!videoMode || !url.trim()) return;
    const controller = new AbortController();
    const timer = window.setTimeout(() => {
      api<Video>("/videos/resolve", {
        method: "POST",
        body: JSON.stringify({ url: url.trim() }),
        signal: controller.signal,
      })
        .then((value) => {
          setPreview(value);
          setError("");
        })
        .catch((e) => {
          if (!controller.signal.aborted) setError(errorText(e));
        });
    }, 600);
    return () => {
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [url, videoMode]);
  async function submit(e: FormEvent) {
    e.preventDefault();
    if (busy || (videoMode ? !url.trim() : !text.trim())) return;
    const content = JSON.stringify({
      kind: videoMode ? "video" : "text",
      text: text.trim(),
      ...(videoMode ? { url: url.trim() } : {}),
    });
    if (pending.current?.content !== content)
      pending.current = { content, id: crypto.randomUUID() };
    setBusy(true);
    setError("");
    try {
      const message = await api<Message>(
        `/conversations/${conversationId}/messages`,
        {
          method: "POST",
          body: JSON.stringify({
            ...JSON.parse(content),
            client_id: pending.current.id,
          }),
        },
      );
      sent(message);
      setText("");
      setUrl("");
      setPreview(null);
      setVideoMode(false);
      pending.current = null;
      if (shared) sharedSent();
    } catch (err) {
      setError(errorText(err));
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="composer-area">
      {error && <ErrorNotice>{error}</ErrorNotice>}
      <form onSubmit={submit} className="composer">
        <div className="composer-top">
          <span>
            <span className="live-dot" /> A LITTLE SOMETHING TO SHARE
          </span>
          <span>Just between you two</span>
        </div>
        {videoMode && (
          <div className="video-input">
            <label>
              <Link2 size={17} />
              <input
                aria-label="Video link"
                type="url"
                required
                placeholder="Paste a TikTok, Reel, or Shorts link"
                maxLength={2048}
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={busy}
              />
            </label>
            <IconButton
              type="button"
              aria-label="Remove video"
              disabled={busy}
              onClick={() => {
                setVideoMode(false);
                setUrl("");
                setError("");
              }}
            >
              <X size={18} />
            </IconButton>
          </div>
        )}
        {preview && (
          <div className="preview-ready">
            <Check size={15} /> {names[preview.platform]} video ready to share
          </div>
        )}
        <div className="composer-main">
          <IconButton
            type="button"
            aria-label="Attach video link"
            title="Attach video link"
            disabled={busy}
            onClick={() => setVideoMode(!videoMode)}
          >
            <Link2 size={22} />
          </IconButton>
          <textarea
            aria-label={videoMode ? "Add a caption" : "Message"}
            placeholder={
              videoMode
                ? "Add a little context…"
                : "Send a message, make their day…"
            }
            rows={1}
            maxLength={4000}
            value={text}
            disabled={busy}
            onChange={(e) => setText(e.target.value)}
            onPaste={(e) => {
              const pasted = e.clipboardData.getData("text").trim();
              if (
                !text &&
                /^https:\/\/(?:www\.|m\.|vm\.|vt\.)?(?:tiktok\.com|instagram\.com|youtube\.com|youtu\.be)\//.test(
                  pasted,
                )
              ) {
                e.preventDefault();
                setVideoMode(true);
                setUrl(pasted);
              }
            }}
            onKeyDown={(e) => {
              if (
                e.key === "Enter" &&
                !e.shiftKey &&
                !e.nativeEvent.isComposing
              ) {
                e.preventDefault();
                void submit(e);
              }
            }}
          />
          <Button
            type="submit"
            aria-label="Send message"
            disabled={busy || (videoMode ? !url.trim() : !text.trim())}
          >
            {busy ? "Sending…" : <Send size={19} />}
          </Button>
        </div>
      </form>
      <p className="composer-hint">
        {videoMode
          ? "Videos play right here in the conversation."
          : "Enter to send · Shift + Enter for a new line · Paste a video link to share"}
      </p>
    </div>
  );
}

function Chat({
  conversation,
  user,
  back,
  shared,
  sharedSent,
  changed,
}: {
  conversation: Conversation;
  user: User;
  back: () => void;
  shared: string;
  sharedSent: () => void;
  changed: () => void;
}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [olderBusy, setOlderBusy] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const [error, setError] = useState("");
  const [profile, setProfile] = useState(false);
  const [newBelow, setNewBelow] = useState(false);
  const list = useRef<HTMLDivElement>(null);
  const nearBottom = useRef(true);
  const count = useRef(0);
  const id = conversation.id;
  useEffect(() => {
    const controller = new AbortController();
    let pending = false;
    let first = true;
    let cursor = 0;
    async function refresh() {
      if (pending || document.hidden) return;
      pending = true;
      try {
        let catchUp = false;
        do {
          const result = await api<{ messages: Message[]; has_more: boolean }>(
            `/conversations/${id}/messages${first ? "" : `?after=${cursor}&limit=100`}`,
            { signal: controller.signal },
          );
          if (controller.signal.aborted) return;
          setMessages((old) =>
            [
              ...new Map(
                [...old, ...result.messages].map((m) => [m.id, m]),
              ).values(),
            ].sort((a, b) => a.id - b.id),
          );
          catchUp = !first && result.has_more;
          if (first) {
            setHasMore(result.has_more);
            first = false;
          }
          cursor = result.messages.at(-1)?.id ?? cursor;
        } while (catchUp);
        setError("");
      } catch (e) {
        if (!controller.signal.aborted) setError(errorText(e));
      } finally {
        pending = false;
        if (!controller.signal.aborted) setLoading(false);
      }
    }
    void refresh();
    const timer = window.setInterval(refresh, 2500);
    document.addEventListener("visibilitychange", refresh);
    return () => {
      controller.abort();
      window.clearInterval(timer);
      document.removeEventListener("visibilitychange", refresh);
    };
  }, [id]);
  useEffect(() => {
    if (messages.length > count.current) {
      if (nearBottom.current) {
        list.current?.scrollTo({ top: list.current.scrollHeight });
        setNewBelow(false);
      } else setNewBelow(true);
    }
    count.current = messages.length;
  }, [messages]);
  async function older() {
    setOlderBusy(true);
    const height = list.current?.scrollHeight || 0;
    try {
      const result = await api<{ messages: Message[]; has_more: boolean }>(
        `/conversations/${id}/messages?before=${messages[0].id}`,
      );
      count.current += result.messages.length;
      setMessages((old) =>
        [
          ...new Map(
            [...result.messages, ...old].map((m) => [m.id, m]),
          ).values(),
        ].sort((a, b) => a.id - b.id),
      );
      setHasMore(result.has_more);
      requestAnimationFrame(() => {
        if (list.current)
          list.current.scrollTop += list.current.scrollHeight - height;
      });
    } catch (e) {
      setError(errorText(e));
    } finally {
      setOlderBusy(false);
    }
  }
  function sent(message: Message) {
    nearBottom.current = true;
    setMessages((old) =>
      [...new Map([...old, message].map((m) => [m.id, m])).values()].sort(
        (a, b) => a.id - b.id,
      ),
    );
    changed();
  }
  return (
    <section className="chat-panel">
      <header className="chat-header">
        <IconButton
          className="mobile-back"
          aria-label="Back to conversations"
          onClick={back}
        >
          <ArrowLeft size={22} />
        </IconButton>
        <Avatar user={conversation.peer} />
        <button className="peer-info" onClick={() => setProfile(true)}>
          <strong>{conversation.peer.display_name}</strong>
          <span>@{conversation.peer.username}</span>
        </button>
        <span className="chat-tag">
          <Film size={16} /> GOOD COMPANY
        </span>
      </header>
      <div
        className="message-list"
        ref={list}
        onScroll={() => {
          if (list.current) {
            nearBottom.current =
              list.current.scrollHeight -
                list.current.scrollTop -
                list.current.clientHeight <
              140;
            if (nearBottom.current) setNewBelow(false);
          }
        }}
      >
        <div className="conversation-start">
          <span className="small-logo">v.</span>
          <p>This is the start of something good.</p>
          <span>Say hello. Share something worth watching.</span>
        </div>
        {loading && (
          <p className="center muted" role="status">
            Loading your conversation…
          </p>
        )}
        {hasMore && (
          <div className="center">
            <OutlineButton disabled={olderBusy} onClick={older}>
              {olderBusy ? "Loading…" : "Earlier messages"}
            </OutlineButton>
          </div>
        )}
        {messages.map((m, index) => (
          <div key={m.id}>
            {(index === 0 ||
              new Date(m.created_at).toDateString() !==
                new Date(messages[index - 1].created_at).toDateString()) && (
              <div className="date-divider">
                {new Date(m.created_at).toLocaleDateString([], {
                  month: "long",
                  day: "numeric",
                })}
              </div>
            )}
            <article
              className={`message ${m.sender_id === user.id ? "mine" : "theirs"}`}
            >
              {m.video && <VideoPlayer video={m.video} />}
              {m.text && <div className="text-bubble">{m.text}</div>}
              <span className="message-meta">
                {time(m.created_at)}
                {m.sender_id === user.id && (
                  <Check size={13} aria-label="Sent" />
                )}
              </span>
            </article>
          </div>
        ))}
      </div>
      {newBelow && (
        <button
          className="new-messages"
          onClick={() => {
            list.current?.scrollTo({
              top: list.current.scrollHeight,
              behavior: "smooth",
            });
            setNewBelow(false);
          }}
        >
          New messages <ArrowDown size={15} />
        </button>
      )}
      {error && (
        <div className="connection-error" role="status">
          {error} Retrying automatically.
        </div>
      )}
      <Composer
        conversationId={id}
        shared={shared}
        sharedSent={sharedSent}
        sent={sent}
      />
      {profile && (
        <Modal
          title={conversation.peer.display_name}
          close={() => setProfile(false)}
        >
          <div className="profile-summary">
            <Avatar user={conversation.peer} />
            <span>@{conversation.peer.username}</span>
          </div>
          <p>
            {conversation.peer.bio || "A good video says a thousand words."}
          </p>
        </Modal>
      )}
    </section>
  );
}

function Workspace({
  user,
  update,
  signedOut,
  shared,
  sharedSent,
}: {
  user: User;
  update: (u: User) => void;
  signedOut: () => void;
  shared: string;
  sharedSent: () => void;
}) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [active, setActive] = useState<Conversation | null>(null);
  const [search, setSearch] = useState("");
  const [newChat, setNewChat] = useState(false);
  const [profile, setProfile] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [online, setOnline] = useState(navigator.onLine);
  const refresh = useCallback(async () => {
    try {
      setConversations(
        (await api<{ conversations: Conversation[] }>("/conversations"))
          .conversations,
      );
      setError("");
    } catch (e) {
      setError(errorText(e));
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    let pending = false;
    const tick = async () => {
      if (!pending && !document.hidden) {
        pending = true;
        await refresh();
        pending = false;
      }
    };
    void tick();
    const timer = window.setInterval(tick, 4000);
    const connectivity = () => setOnline(navigator.onLine);
    window.addEventListener("online", connectivity);
    window.addEventListener("offline", connectivity);
    return () => {
      window.clearInterval(timer);
      window.removeEventListener("online", connectivity);
      window.removeEventListener("offline", connectivity);
    };
  }, [refresh]);
  async function logout() {
    try {
      await api("/auth/logout", { method: "POST", body: "{}" });
      signedOut();
    } catch (e) {
      setError(errorText(e));
    }
  }
  const selected = conversations.find((c) => c.id === active?.id) || active;
  const filtered = conversations.filter((c) =>
    `${c.peer.display_name} ${c.peer.username}`
      .toLowerCase()
      .includes(search.toLowerCase()),
  );
  return (
    <main className={`app-shell ${selected ? "has-chat" : ""}`}>
      <nav className="rail" aria-label="Main navigation">
        <span className="brand-mark">
          v<span>·</span>
        </span>
        <div className="rail-middle">
          <IconButton
            aria-label="Conversations"
            className="rail-selected"
            onClick={() => setActive(null)}
          >
            <MessageCircle size={23} />
          </IconButton>
          <IconButton
            aria-label="New conversation"
            onClick={() => setNewChat(true)}
          >
            <Plus size={24} />
          </IconButton>
        </div>
        <IconButton aria-label="Edit profile" onClick={() => setProfile(true)}>
          <Settings2 size={22} />
        </IconButton>
        <button
          className="avatar-button"
          aria-label="Open your profile"
          onClick={() => setProfile(true)}
        >
          <Avatar user={user} small />
        </button>
      </nav>
      <aside className="sidebar">
        <header className="sidebar-header">
          <div className="sidebar-topbar">
            <Logo />
            <ThemeSelect />
          </div>
          <div className="sidebar-title">
            <h1>
              Conversations
              <span>{conversations.length.toString().padStart(2, "0")}</span>
            </h1>
            <IconButton
              aria-label="Start a conversation"
              onClick={() => setNewChat(true)}
            >
              <Plus size={23} />
            </IconButton>
          </div>
          <label className="search-field">
            <Search size={18} />
            <input
              aria-label="Filter conversations"
              placeholder="Find a conversation"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </label>
        </header>
        {shared && (
          <div className="share-notice">
            <Film size={19} />
            <span>
              A video came along with you.
              <br />
              Choose someone to share it with.
            </span>
          </div>
        )}
        {!online && (
          <div className="connection-error">
            You’re offline. Messages need a connection.
          </div>
        )}
        {error && (
          <div className="connection-error" role="status">
            {error}
          </div>
        )}
        <div className="conversation-list">
          <span className="list-label">YOUR PEOPLE</span>
          {loading && <p className="sidebar-empty">Loading conversations…</p>}
          {filtered.map((c) => (
            <button
              className={`conversation-row ${selected?.id === c.id ? "active" : ""}`}
              key={c.id}
              onClick={() => setActive(c)}
            >
              <Avatar user={c.peer} />
              <span className="conversation-info">
                <span>
                  <strong>{c.peer.display_name}</strong>
                  <time>{time(c.updated_at)}</time>
                </span>
                <small>
                  {c.last_kind === "video"
                    ? "↗ Shared a video"
                    : c.last_text || "Say hello 👋"}
                </small>
              </span>
            </button>
          ))}
          {!loading && !filtered.length && (
            <div className="sidebar-empty">
              <MessageCircle size={28} />
              <p>
                {search
                  ? "No conversations match."
                  : "Your next favorite conversation starts here."}
              </p>
              <button className="text-button" onClick={() => setNewChat(true)}>
                Find someone <ArrowRight size={15} />
              </button>
            </div>
          )}
        </div>
        <footer className="sidebar-footer">
          <button onClick={() => setProfile(true)}>
            <Avatar user={user} small />
            <span>
              <strong>{user.display_name}</strong>
              <small>@{user.username}</small>
            </span>
          </button>
          <IconButton aria-label="Sign out" onClick={logout}>
            <LogOut size={19} />
          </IconButton>
        </footer>
      </aside>
      {selected ? (
        <Chat
          key={selected.id}
          conversation={selected}
          user={user}
          back={() => setActive(null)}
          shared={shared}
          sharedSent={sharedSent}
          changed={refresh}
        />
      ) : (
        <section className="welcome-panel">
          <div className="welcome-top">
            <span className="eyebrow">A LITTLE CLOSER, EVEN FROM HERE</span>
            <span className="edition">EST. 2026</span>
          </div>
          <div className="welcome-content">
            <div className="welcome-illustration">
              <span className="welcome-card">
                <Film size={46} strokeWidth={1.2} />
              </span>
              <span className="welcome-chat">
                <MessageCircle size={28} />
              </span>
              <Sparkles className="welcome-spark" size={28} />
            </div>
            <span className="eyebrow">WELCOME TO YOUR CORNER</span>
            <h2>
              Good videos.
              <br />
              <em>Better conversations.</em>
            </h2>
            <p>
              {shared
                ? "Your video is ready. Choose a conversation or find someone to send it to."
                : "The clip that made you laugh. The place you want to go. The little things that bring you closer."}
            </p>
            <Button onClick={() => setNewChat(true)}>
              <Plus size={18} />
              Start a conversation
            </Button>
            <div className="platform-row">
              <span>TikTok</span>
              <span>Instagram</span>
              <span>YouTube Shorts</span>
            </div>
          </div>
          <footer className="welcome-footer">
            <Link2 size={16} /> ONE CONVERSATION. EVERY PLATFORM.
          </footer>
        </section>
      )}
      {newChat && (
        <NewChat
          close={() => setNewChat(false)}
          opened={(c) => {
            setActive(c);
            void refresh();
          }}
        />
      )}
      {profile && (
        <Profile user={user} close={() => setProfile(false)} update={update} />
      )}
    </main>
  );
}

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [shared, setShared] = useState(sharedLink);
  const load = useCallback(async () => {
    setError("");
    setLoading(true);
    try {
      setUser((await api<{ user: User }>("/me")).user);
    } catch (e) {
      if (!(e instanceof ApiError && e.status === 401)) setError(errorText(e));
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    void load();
    const expired = () => setUser(null);
    window.addEventListener("session-expired", expired);
    return () => window.removeEventListener("session-expired", expired);
  }, [load]);
  if (loading)
    return (
      <div className="boot">
        <ThemeSelect />
        <Logo />
        <p>Getting your corner ready…</p>
      </div>
    );
  if (error)
    return (
      <div className="boot">
        <ThemeSelect />
        <Logo />
        <ErrorNotice>{error}</ErrorNotice>
        <Button onClick={load}>Try again</Button>
      </div>
    );
  return user ? (
    <Workspace
      user={user}
      update={setUser}
      signedOut={() => setUser(null)}
      shared={shared}
      sharedSent={() => {
        setShared("");
        sessionStorage.removeItem("vertical-share");
      }}
    />
  ) : (
    <Auth signedIn={setUser} shared={shared} />
  );
}
