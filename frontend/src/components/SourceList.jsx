import { getDomain, getFaviconUrl, formatSourceTitle, sourceKey } from "../lib/conversations";

export default function SourceList({ sources }) {
  if (!sources?.length) {
    return null;
  }

  return (
    <div className="sources" aria-label="Sources">
      <span className="sources-label">Sources</span>
      <div className="source-strip">
        {sources.map((source, index) => {
          const url = source.url || source.canonical_url;
          const title = formatSourceTitle(source);
          const domain = url ? getDomain(url) : "juit.ac.in";
          const faviconUrl = url ? getFaviconUrl(url) : "/favicon.svg";

          const sourceContent = (
            <>
              <span className="source-index">{index + 1}</span>
              <span className="source-favicon" aria-hidden="true">
                <img
                  src={faviconUrl}
                  alt=""
                  loading="lazy"
                  onError={(event) => {
                    event.currentTarget.style.display = "none";
                  }}
                />
              </span>
              <span className="source-text">
                <span className="source-title">{title}</span>
                <span className="source-domain">{domain}</span>
              </span>
              {url && (
                <span className="source-external" aria-hidden="true">
                  ↗
                </span>
              )}
            </>
          );

          return (
            <article className="source-chip" key={sourceKey(source, index)}>
              {url ? (
                <a
                  href={url}
                  target="_blank"
                  rel="noreferrer"
                  title={`${title} - ${url}`}
                  aria-label={`Open source ${index + 1}: ${title}`}
                >
                  {sourceContent}
                </a>
              ) : (
                <div>{sourceContent}</div>
              )}
            </article>
          );
        })}
      </div>
    </div>
  );
}
