"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

const fieldStyles =
  "w-full border border-border bg-transparent px-4 py-3 text-sm text-ink placeholder:text-muted focus:border-accent focus:outline-none";

type Status = "idle" | "submitting" | "success" | "error";

/**
 * Submits to /api/contact, which delivers the message by email via
 * Resend. See that route for the required environment variables.
 */
export function ContactForm() {
  const [status, setStatus] = useState<Status>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("submitting");
    setErrorMessage(null);

    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form).entries());

    try {
      const response = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(body?.error ?? "The message could not be sent.");
      }

      setStatus("success");
    } catch (error) {
      setStatus("error");
      setErrorMessage(error instanceof Error ? error.message : "The message could not be sent.");
    }
  }

  if (status === "success") {
    return (
      <div className="border border-border p-8">
        <p className="text-base text-ink">
          Thank you. Your message has been received, and you&apos;ll hear back directly within a few business days.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6" noValidate>
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div>
          <label htmlFor="name" className="text-eyebrow uppercase tracking-widest text-muted">
            Name
          </label>
          <input id="name" name="name" type="text" required className={`mt-2 ${fieldStyles}`} placeholder="Jane Doe" />
        </div>
        <div>
          <label htmlFor="organization" className="text-eyebrow uppercase tracking-widest text-muted">
            Organisation
          </label>
          <input
            id="organization"
            name="organization"
            type="text"
            className={`mt-2 ${fieldStyles}`}
            placeholder="Organisation name"
          />
        </div>
        <div>
          <label htmlFor="role" className="text-eyebrow uppercase tracking-widest text-muted">
            Role
          </label>
          <input id="role" name="role" type="text" className={`mt-2 ${fieldStyles}`} placeholder="CISO, Board Member, etc." />
        </div>
        <div>
          <label htmlFor="email" className="text-eyebrow uppercase tracking-widest text-muted">
            Email
          </label>
          <input id="email" name="email" type="email" required className={`mt-2 ${fieldStyles}`} placeholder="jane@company.com" />
        </div>
      </div>

      <div>
        <label htmlFor="message" className="text-eyebrow uppercase tracking-widest text-muted">
          Message
        </label>
        <textarea
          id="message"
          name="message"
          rows={5}
          required
          className={`mt-2 ${fieldStyles}`}
          placeholder="What are you working through right now?"
        />
      </div>

      {/* Honeypot: hidden from real visitors, filled in only by bots. */}
      <input type="text" name="company" tabIndex={-1} autoComplete="off" className="hidden" aria-hidden="true" />

      {status === "error" && <p className="text-sm text-signal">{errorMessage}</p>}

      <Button type="submit" variant="primary" size="lg" disabled={status === "submitting"}>
        {status === "submitting" ? "Sending…" : "Send message"}
      </Button>
    </form>
  );
}
