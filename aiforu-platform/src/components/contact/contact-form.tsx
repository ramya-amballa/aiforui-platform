"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

const fieldStyles =
  "w-full border border-border bg-transparent px-4 py-3 text-sm text-ink placeholder:text-muted focus:border-accent focus:outline-none";

/**
 * Presentational contact form. Submission wiring (API route / provider)
 * is out of scope for Phase 1; see README "Remaining Work".
 */
export function ContactForm() {
  const [submitted, setSubmitted] = useState(false);

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitted(true);
  }

  if (submitted) {
    return (
      <div className="border border-border p-8">
        <p className="text-base text-ink">Thank you. Your message has been received, and you&apos;ll hear back directly within a few business days.</p>
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

      <Button type="submit" variant="primary" size="lg">
        Send message
      </Button>
    </form>
  );
}
