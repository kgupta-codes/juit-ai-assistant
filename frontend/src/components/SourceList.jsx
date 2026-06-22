import { getDomain, sourceKey } from "../lib/conversations";
import { DocumentIcon } from "./icons";

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
          const title = source.title || "JUIT source";
          const domain = url ? getDomain(url) : "juit.ac.in";

          const sourceContent = (
            <>
              <span className="source-index">{index + 1}</span>
              <span className="source-icon" aria-hidden="true">
                <DocumentIcon />
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
                <a href={url} target="_blank" rel="noreferrer" title={url}>
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
