import type { FC } from "react";

type BookCardProps = {
  title: string;
  author: string;
  description?: string;
  coverUrl?: string;
  reason?: string;
  tropes?: string[];
  scoreLabel?: string;
  onLike?: () => void;
  onSkip?: () => void;
  disabled?: boolean;
};

const BookCard: FC<BookCardProps> = ({
  title,
  author,
  description,
  coverUrl,
  reason,
  tropes,
  scoreLabel,
  onLike,
  onSkip,
  disabled
}) => {
  return (
    <article className="book-card">
      {coverUrl ? (
        <img src={coverUrl} alt={`Cover of ${title}`} loading="lazy" />
      ) : (
        <div style={{ height: "320px", background: "linear-gradient(135deg,#6366f1,#ec4899)" }} />
      )}
      <div className="book-card-content">
        <header>
          <h2 style={{ margin: 0, fontSize: "1.5rem", color: "#111827" }}>{title}</h2>
          <p style={{ margin: "0.25rem 0", color: "#6b7280" }}>by {author}</p>
        </header>
        {scoreLabel && (
          <p style={{ margin: 0, fontSize: "0.75rem", textTransform: "uppercase", color: "#0ea5e9" }}>{scoreLabel}</p>
        )}
        {tropes && tropes.length > 0 && (
          <div className="trope-badges" aria-label="Matched tropes">
            {tropes.map((trope) => (
              <span key={trope} className="trope-badge">
                {trope}
              </span>
            ))}
          </div>
        )}
        {reason && (
          <p style={{ margin: "0.5rem 0", color: "#3730a3", fontWeight: 600 }}>{reason}</p>
        )}
        {description && (
          <p style={{ margin: 0, color: "#4b5563", fontSize: "0.95rem" }}>{description}</p>
        )}
        <div className="book-card-actions">
          <button className="secondary-button" type="button" onClick={onSkip} disabled={disabled}>
            Skip
          </button>
          <button className="primary-button" type="button" onClick={onLike} disabled={disabled}>
            Save
          </button>
        </div>
      </div>
    </article>
  );
};

export type { BookCardProps };
export default BookCard;
