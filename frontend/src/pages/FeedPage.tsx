import { useCallback, useEffect, useMemo, useState } from "react";
import BookCard from "../components/BookCard";
import { apiRequest } from "../hooks/useApi";

type FeedMode = "taste" | "trope";

type TasteRecommendationResponse = {
  id: number;
  score: number;
  explanation?: string;
  generated_at: string;
  book: {
    id: number;
    title: string;
    author: string;
    description?: string;
    cover_url?: string;
    reason?: string;
  };
};

type RecommendationsResponse = {
  items: TasteRecommendationResponse[];
};

type TropeRecommendation = {
  id: string;
  title: string;
  author: string;
  description?: string;
  cover_url?: string;
  matched_tropes: string[];
  all_tropes: string[];
  score: number;
  explanation: string;
};

type TropeRecommendationsResponse = {
  items: TropeRecommendation[];
};

type CardViewModel = {
  id: string;
  title: string;
  author: string;
  description?: string;
  coverUrl?: string;
  reason?: string;
  tropes?: string[];
  scoreLabel?: string;
  feedbackBookId?: number;
};

const FeedPage = () => {
  const [mode, setMode] = useState<FeedMode>("taste");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<CardViewModel[]>([]);
  const [activeIndex, setActiveIndex] = useState(0);
  const [feedbackState, setFeedbackState] = useState<Record<string, "liked" | "skipped">>({});

  const activeRecommendation = useMemo(
    () => recommendations[activeIndex],
    [recommendations, activeIndex]
  );

  const normaliseTasteFeed = useCallback((payload: RecommendationsResponse): CardViewModel[] => {
    return payload.items.map((item) => ({
      id: `taste-${item.id}`,
      title: item.book.title,
      author: item.book.author,
      description: item.book.description,
      coverUrl: item.book.cover_url,
      reason: item.explanation || item.book.reason,
      scoreLabel: `Affinity ${Math.round(item.score * 100)}%`,
      feedbackBookId: item.book.id
    }));
  }, []);

  const normaliseTropeFeed = useCallback((payload: TropeRecommendationsResponse): CardViewModel[] => {
    return payload.items.map((item) => ({
      id: `trope-${item.id}`,
      title: item.title,
      author: item.author,
      description: item.description,
      coverUrl: item.cover_url,
      reason: item.explanation,
      tropes: item.matched_tropes.length > 0 ? item.matched_tropes : item.all_tropes,
      scoreLabel: `Trope match ${item.score}%`
    }));
  }, []);

  const loadRecommendations = useCallback(
    async (selectedMode: FeedMode) => {
      setLoading(true);
      setError(null);
      try {
        if (selectedMode === "trope") {
          const data = await apiRequest<TropeRecommendationsResponse>("/api/discovery/trope-feed?limit=10");
          setRecommendations(normaliseTropeFeed(data));
        } else {
          const data = await apiRequest<RecommendationsResponse>("/api/recommendations?limit=10");
          setRecommendations(normaliseTasteFeed(data));
        }
        setActiveIndex(0);
        setFeedbackState({});
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch recommendations");
      } finally {
        setLoading(false);
      }
    },
    [normaliseTasteFeed, normaliseTropeFeed]
  );

  useEffect(() => {
    void loadRecommendations(mode);
  }, [loadRecommendations, mode]);

  const handleAdvance = useCallback(() => {
    setActiveIndex((current) => (current + 1 < recommendations.length ? current + 1 : current));
  }, [recommendations.length]);

  const submitFeedback = useCallback(
    async (reaction: "like" | "skip") => {
      const current = activeRecommendation;
      if (!current) return;
      const stateKey = current.id;
      setFeedbackState((prev) => ({ ...prev, [stateKey]: reaction === "like" ? "liked" : "skipped" }));
      if (current.feedbackBookId) {
        try {
          await apiRequest("/api/feedback", {
            method: "POST",
            body: JSON.stringify({
              book_id: current.feedbackBookId,
              reaction: reaction === "like" ? "liked" : "skipped"
            })
          });
        } catch (err) {
          console.error(err);
        }
      }
      handleAdvance();
    },
    [activeRecommendation, handleAdvance]
  );

  if (loading) {
    return <div className="status-banner">Loading recommendations…</div>;
  }

  if (error) {
    return (
      <div className="empty-state">
        <p>{error}</p>
        <button className="primary-button" type="button" onClick={() => loadRecommendations(mode)}>
          Retry
        </button>
      </div>
    );
  }

  if (!activeRecommendation) {
    return (
      <div className="empty-state">
        <p>No recommendations yet. Try running a sync or trope extraction from Settings.</p>
        <button className="primary-button" type="button" onClick={() => loadRecommendations(mode)}>
          Refresh
        </button>
      </div>
    );
  }

  return (
    <div className="card-stack">
      <div className="feed-toggle" role="tablist" aria-label="Recommendation sources">
        <button
          type="button"
          role="tab"
          className={`toggle-button ${mode === "taste" ? "active" : ""}`}
          onClick={() => setMode("taste")}
          aria-selected={mode === "taste"}
        >
          Taste Feed
        </button>
        <button
          type="button"
          role="tab"
          className={`toggle-button ${mode === "trope" ? "active" : ""}`}
          onClick={() => setMode("trope")}
          aria-selected={mode === "trope"}
        >
          Trope Feed
        </button>
      </div>
      <BookCard
        key={activeRecommendation.id}
        title={activeRecommendation.title}
        author={activeRecommendation.author}
        description={activeRecommendation.description}
        coverUrl={activeRecommendation.coverUrl}
        reason={activeRecommendation.reason}
        tropes={activeRecommendation.tropes}
        scoreLabel={activeRecommendation.scoreLabel}
        onLike={() => submitFeedback("like")}
        onSkip={() => submitFeedback("skip")}
        disabled={feedbackState[activeRecommendation.id] !== undefined}
      />
    </div>
  );
};

export default FeedPage;
