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
    } else if (token.startsWith("[")) {
      const linkMatch = token.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
      if (linkMatch) {
        tokens.push(
          <a key={key} href={linkMatch[2]} target="_blank" rel="noreferrer">
            {linkMatch[1]}
          </a>,
        );
      } else {
        tokens.push(token);
      }
    }

    lastIndex = pattern.lastIndex;
  }

  if (lastIndex < text.length) {
    tokens.push(text.slice(lastIndex));
  }

  return tokens;
}

export function renderMarkdownBlocks(text) {
  const blocks = [];
  const lines = text.split("\n");
  let paragraph = [];
  let listItems = null;
  let listType = "ul";

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
    if (!listItems || listItems.length === 0) {
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

  lines.forEach((rawLine) => {
    const line = rawLine.trim();

    if (!line) {
      flushParagraph();
      flushList();
      return;
    }

    const unordered = line.match(/^[-*]\s+(.*)$/);
    const ordered = line.match(/^\d+\.\s+(.*)$/);

    if (unordered || ordered) {
      flushParagraph();
      if (!listItems) {
        listItems = [];
        listType = ordered ? "ol" : "ul";
      }

      listItems.push((unordered || ordered)[1]);
      return;
    }

    flushList();
    paragraph.push(line);
  });

  flushParagraph();
  flushList();

  if (blocks.length === 0) {
    return <p>{renderInlineMarkdown(text)}</p>;
  }

  return blocks;
}
