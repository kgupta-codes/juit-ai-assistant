function renderInlineMarkdown(text) {
  const tokens = [];
  const pattern = /(\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))/g;
  let lastIndex = 0;
  let match;

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      tokens.push(text.slice(lastIndex, match.index));
    }

    const token = match[0];
    const key = `${match.index}-${token}`;

    if (token.startsWith("**")) {
      tokens.push(<strong key={key}>{token.slice(2, -2)}</strong>);
    } else if (token.startsWith("`")) {
      tokens.push(<code key={key}>{token.slice(1, -1)}</code>);
    } else {
      const linkMatch = token.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
      tokens.push(
        linkMatch ? (
          <a key={key} href={linkMatch[2]} target="_blank" rel="noreferrer">
            {linkMatch[1]}
          </a>
        ) : (
          token
        ),
      );
    }

    lastIndex = pattern.lastIndex;
  }

  if (lastIndex < text.length) {
    tokens.push(text.slice(lastIndex));
  }

  return tokens;
}

function isTableDivider(line) {
  return /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line);
}

function parseTableRow(line) {
  return line
    .trim()
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((cell) => cell.trim());
}

function renderCodeBlock(code, language, key) {
  return (
    <pre className="code-block" key={key}>
      {language ? <span className="code-language">{language}</span> : null}
      <code>{code}</code>
    </pre>
  );
}

function renderTableBlock(header, rows, key) {
  return (
    <div className="markdown-table-wrap" key={key}>
      <table>
        <thead>
          <tr>
            {header.map((cell, index) => (
              <th key={`${cell}-${index}`}>{renderInlineMarkdown(cell)}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={`row-${rowIndex}`}>
              {row.map((cell, cellIndex) => (
                <td key={`${cell}-${cellIndex}`}>{renderInlineMarkdown(cell)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function renderMarkdownBlocks(text = "") {
  const blocks = [];
  const lines = String(text).split("\n");
  let paragraph = [];
  let listItems = null;
  let listType = "ul";
  let codeLines = null;
  let codeLanguage = "";

  const flushParagraph = () => {
    if (paragraph.length === 0) {
      return;
    }

    blocks.push(
      <p key={`paragraph-${blocks.length}`}>{renderInlineMarkdown(paragraph.join(" "))}</p>,
    );
    paragraph = [];
  };

  const flushList = () => {
    if (!listItems?.length) {
      return;
    }

    const ListTag = listType === "ol" ? "ol" : "ul";
    blocks.push(
      <ListTag key={`list-${blocks.length}`}>
        {listItems.map((item, index) => (
          <li key={`${item}-${index}`}>{renderInlineMarkdown(item)}</li>
        ))}
      </ListTag>,
    );
    listItems = null;
  };

  for (let index = 0; index < lines.length; index += 1) {
    const rawLine = lines[index];
    const line = rawLine.trim();

    if (line.startsWith("```")) {
      if (codeLines) {
        blocks.push(renderCodeBlock(codeLines.join("\n"), codeLanguage, `code-${blocks.length}`));
        codeLines = null;
        codeLanguage = "";
      } else {
        flushParagraph();
        flushList();
        codeLines = [];
        codeLanguage = line.slice(3).trim();
      }
      continue;
    }

    if (codeLines) {
      codeLines.push(rawLine);
      continue;
    }

    if (!line) {
      flushParagraph();
      flushList();
      continue;
    }

    if (index + 1 < lines.length && isTableDivider(lines[index + 1])) {
      flushParagraph();
      flushList();
      const header = parseTableRow(line);
      const rows = [];
      index += 2;

      while (index < lines.length && lines[index].includes("|")) {
        rows.push(parseTableRow(lines[index]));
        index += 1;
      }

      index -= 1;
      blocks.push(renderTableBlock(header, rows, `table-${blocks.length}`));
      continue;
    }

    const heading = line.match(/^(#{1,3})\s+(.*)$/);
    if (heading) {
      flushParagraph();
      flushList();
      const HeadingTag = `h${heading[1].length + 2}`;
      blocks.push(
        <HeadingTag key={`heading-${blocks.length}`}>
          {renderInlineMarkdown(heading[2])}
        </HeadingTag>,
      );
      continue;
    }

    const quote = line.match(/^>\s?(.*)$/);
    if (quote) {
      flushParagraph();
      flushList();
      blocks.push(
        <blockquote key={`quote-${blocks.length}`}>
          {renderInlineMarkdown(quote[1])}
        </blockquote>,
      );
      continue;
    }

    const unordered = line.match(/^[-*]\s+(.*)$/);
    const ordered = line.match(/^\d+\.\s+(.*)$/);

    if (unordered || ordered) {
      flushParagraph();
      if (!listItems || (ordered && listType !== "ol") || (unordered && listType !== "ul")) {
        flushList();
        listItems = [];
        listType = ordered ? "ol" : "ul";
      }

      listItems.push((unordered || ordered)[1]);
      continue;
    }

    flushList();
    paragraph.push(line);
  }

  if (codeLines) {
    blocks.push(renderCodeBlock(codeLines.join("\n"), codeLanguage, `code-${blocks.length}`));
  }
  flushParagraph();
  flushList();

  return blocks.length ? blocks : <p>{renderInlineMarkdown(text)}</p>;
}
