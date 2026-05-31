import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ScoreRing } from "@/components/shared/score-ring";

describe("ScoreRing", () => {
  it("renders the rounded score", () => {
    render(<ScoreRing score={87.4} />);
    expect(screen.getByText("87")).toBeInTheDocument();
  });
});

