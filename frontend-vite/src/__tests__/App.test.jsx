import { render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import App from "../App.jsx";

describe("App", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: {
        get: () => "application/json"
      },
      json: async () => [],
      text: async () => ""
    });
    window.localStorage.clear();
  });

  it("renders the header and default catalog page", async () => {
    render(<App />);

    expect(screen.getByText(/StoryShelf Console/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Catalog" })).toBeInTheDocument();

    await waitFor(() => expect(globalThis.fetch).toHaveBeenCalled());
    expect(globalThis.fetch).toHaveBeenCalledWith(
      "/api/v1/books",
      expect.objectContaining({ method: "GET" })
    );

    expect(screen.getByRole("heading", { name: "Catalog" })).toBeInTheDocument();
  });
});
