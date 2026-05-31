import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ExportButtons } from "@/features/export/export-buttons";

describe("ExportButtons", () => {
  it("links to CSV and Excel downloads", () => {
    render(<ExportButtons />);
    expect(screen.getByRole("link", { name: /csv/i })).toHaveAttribute("href", expect.stringContaining("/download/csv"));
    expect(screen.getByRole("link", { name: /excel/i })).toHaveAttribute("href", expect.stringContaining("/download/excel"));
  });
});

