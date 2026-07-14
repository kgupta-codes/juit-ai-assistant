export function LogoMark({ compact = false }) {
  return (
    <div className={`logo-mark${compact ? " compact" : ""}`}>
      <img className="logo-icon" src="/juit-mark.png" alt="JUIT logo" />
    </div>
  );
}

export function PlusIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M11 5h2v14h-2z" />
      <path d="M5 11h14v2H5z" />
    </svg>
  );
}

export function SendIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M4 20V4l18 8-18 8Zm2.7-3.2L17.1 12 6.7 7.2V10l4 2-4 2v2.8Z" />
    </svg>
  );
}

export function SunIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 5.5A6.5 6.5 0 1 0 18.5 12 6.51 6.51 0 0 0 12 5.5Zm0 11A4.5 4.5 0 1 1 16.5 12 4.5 4.5 0 0 1 12 16.5ZM11 1h2v3h-2Zm0 19h2v3h-2ZM1 11h3v2H1Zm19 0h3v2h-3ZM4.2 4.2l1.4-1.4 2.1 2.1-1.4 1.4Zm12.1 12.1 1.4-1.4 2.1 2.1-1.4 1.4ZM17.7 4.2l2.1-2.1 1.4 1.4-2.1 2.1ZM4.2 19.8l2.1-2.1 1.4 1.4-2.1 2.1Z" />
    </svg>
  );
}

export function MoonIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M20 14.3A8.8 8.8 0 0 1 9.7 4a9 9 0 1 0 10.3 10.3Z" />
    </svg>
  );
}

export function DocumentIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M7 2h7l5 5v15a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm6 1.5V8h4.5" />
      <path d="M8 12h8v2H8Zm0 4h8v2H8Zm0-8h4v2H8Z" />
    </svg>
  );
}

export function SparkIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="m12 2 1.8 6.2L20 10l-6.2 1.8L12 18l-1.8-6.2L4 10l6.2-1.8L12 2Zm6.2 12.8.8 2.7 2.8.8-2.8.8-.8 2.9-.8-2.9-2.9-.8 2.9-.8.8-2.7ZM5.4 14l.7 2.3 2.3.7-2.3.7-.7 2.3-.7-2.3-2.3-.7 2.3-.7.7-2.3Z" />
    </svg>
  );
}

export function MenuIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M4 7h16v2H4Zm0 4.5h16v2H4ZM4 16h16v2H4Z" />
    </svg>
  );
}

export function CloseIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M6.2 5 5 6.2 10.8 12 5 17.8 6.2 19 12 13.2 17.8 19 19 17.8 13.2 12 19 6.2 17.8 5 12 10.8Z" />
    </svg>
  );
}

export function CopyIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M8 7a3 3 0 0 1 3-3h7a3 3 0 0 1 3 3v7a3 3 0 0 1-3 3h-1v-2h1a1 1 0 0 0 1-1V7a1 1 0 0 0-1-1h-7a1 1 0 0 0-1 1v1H8V7Z" />
      <path d="M6 9h7a3 3 0 0 1 3 3v7a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3v-7a3 3 0 0 1 3-3Zm0 2a1 1 0 0 0-1 1v7a1 1 0 0 0 1 1h7a1 1 0 0 0 1-1v-7a1 1 0 0 0-1-1H6Z" />
    </svg>
  );
}

export function RefreshIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M17.7 6.3A8 8 0 0 0 4.2 10H2a10 10 0 0 1 17.1-5.1L21 3v6h-6l2.7-2.7ZM6.3 17.7A8 8 0 0 0 19.8 14H22A10 10 0 0 1 4.9 19.1L3 21v-6h6l-2.7 2.7Z" />
    </svg>
  );
}

export function StopIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M7 7h10v10H7z" />
    </svg>
  );
}

export function SearchIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M10.5 3a7.5 7.5 0 0 1 5.9 12.1l4.2 4.2-1.4 1.4-4.2-4.2A7.5 7.5 0 1 1 10.5 3Zm0 2a5.5 5.5 0 1 0 0 11 5.5 5.5 0 0 0 0-11Z" />
    </svg>
  );
}

export function EditIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M17.8 3.2a2.8 2.8 0 0 1 4 4L8.7 20.3 3 21l.7-5.7L17.8 3.2Zm2.6 1.4a.8.8 0 0 0-1.2 0L18 5.8 19.2 7l1.2-1.2a.8.8 0 0 0 0-1.2ZM5.6 16.2l-.3 2.5 2.5-.3 10-10L16 6.6l-10.4 9.6Z" />
    </svg>
  );
}

export function TrashIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M9 3h6l1 2h5v2H3V5h5l1-2Zm-3 6h12l-.8 12H6.8L6 9Zm2.1 2 .5 8h6.8l.5-8H8.1Z" />
    </svg>
  );
}

export function CheckIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="m9.2 16.6-4.4-4.4-1.4 1.4 5.8 5.8L21 7.6l-1.4-1.4L9.2 16.6Z" />
    </svg>
  );
}

export function TopicIcon({ label }) {
  switch (label) {
    case "Admissions":
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 2 2.7 6.7 12 11.3l9.3-4.6L12 2Zm0 9.3L4 7.2V16l8 4 8-4V7.2l-8 4.1Z" />
        </svg>
      );
    case "Placements":
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M9 4h6l1 3h3a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h3l1-3Zm1.5 3h3l-.5-1.5h-2L10.5 7Z" />
        </svg>
      );
    case "Research Centers":
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M9 3h6v2l-1 1v3.2l4.9 7.3A3 3 0 0 1 16.4 21H7.6a3 3 0 0 1-2.5-4.8L10 9.2V6L9 5V3Zm1.8 8-4.2 6.2A1 1 0 0 0 7.6 19h8.8a1 1 0 0 0 .8-1.5L13 11h-2.2Z" />
        </svg>
      );
    case "Scholarships":
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 2 9.2 8 3 9l4.5 4.3L6.4 20 12 17l5.6 3-1.1-6.7L21 9l-6.2-1L12 2Z" />
        </svg>
      );
    case "Hostels":
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M4 10h16v12H4Zm2-6h12v4H6Zm2 8h4v4H8Zm6 0h2v2h-2Zm0 4h2v2h-2Z" />
        </svg>
      );
    default:
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 2 2.7 6.7 12 11.3l9.3-4.6L12 2Zm0 9.3L4 7.2V16l8 4 8-4V7.2l-8 4.1Z" />
        </svg>
      );
  }
}
