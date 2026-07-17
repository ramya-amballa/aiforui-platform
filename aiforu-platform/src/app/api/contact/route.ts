import { NextResponse } from "next/server";
import { Resend } from "resend";

/**
 * Delivers contact form submissions by email via Resend. Requires
 * RESEND_API_KEY and CONTACT_TO_EMAIL as environment variables in
 * Vercel; without them the route responds with a clear 500 rather than
 * silently discarding the submission.
 *
 * The sender defaults to Resend's shared onboarding address, which
 * only delivers to the email that owns the Resend account. Once the
 * aiforui.org domain is verified in Resend, replace RESEND_FROM_EMAIL
 * with a branded sender (e.g. contact@aiforui.org) to lift that limit.
 */
export async function POST(request: Request) {
  const apiKey = process.env.RESEND_API_KEY;
  const toEmail = process.env.CONTACT_TO_EMAIL;

  if (!apiKey || !toEmail) {
    console.error("Contact form is not configured: missing RESEND_API_KEY or CONTACT_TO_EMAIL.");
    return NextResponse.json(
      { error: "The contact form is not yet configured. Please try again later." },
      { status: 500 },
    );
  }

  const body = await request.json().catch(() => null);
  if (!body) {
    return NextResponse.json({ error: "Invalid submission." }, { status: 400 });
  }

  const { name, organization, role, email, message, company } = body as Record<string, string | undefined>;

  // Honeypot: real visitors never fill in this hidden field.
  if (company) {
    return NextResponse.json({ ok: true });
  }

  if (!name || !email || !message) {
    return NextResponse.json({ error: "Name, email and message are required." }, { status: 400 });
  }

  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailPattern.test(email)) {
    return NextResponse.json({ error: "Please provide a valid email address." }, { status: 400 });
  }

  const resend = new Resend(apiKey);
  const fromEmail = process.env.RESEND_FROM_EMAIL ?? "AI for U&I Contact Form <onboarding@resend.dev>";

  const { error } = await resend.emails.send({
    from: fromEmail,
    to: toEmail,
    replyTo: email,
    subject: `New contact form submission from ${name}`,
    text: [
      `Name: ${name}`,
      organization ? `Organisation: ${organization}` : null,
      role ? `Role: ${role}` : null,
      `Email: ${email}`,
      "",
      message,
    ]
      .filter(Boolean)
      .join("\n"),
  });

  if (error) {
    console.error("Resend failed to send contact form email:", error);
    return NextResponse.json({ error: "The message could not be sent. Please try again." }, { status: 502 });
  }

  return NextResponse.json({ ok: true });
}
