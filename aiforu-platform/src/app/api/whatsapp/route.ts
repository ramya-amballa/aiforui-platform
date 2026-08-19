import { NextResponse } from "next/server";

/**
 * Redirects to a WhatsApp click-to-chat link without ever putting the
 * phone number in the site's HTML/JS bundle — it's read server-side
 * from WHATSAPP_NUMBER and only resolved into a wa.me URL at the
 * moment someone actually clicks. Requires WHATSAPP_NUMBER as an
 * environment variable in Vercel (see .env.example, digits only, no
 * "+" or spaces, e.g. "919392696371"); without it, falls back to the
 * contact form instead of failing visibly.
 */
export async function GET(request: Request) {
  const number = process.env.WHATSAPP_NUMBER;

  if (!number) {
    console.error("WhatsApp chat link requested but WHATSAPP_NUMBER is not configured.");
    return NextResponse.redirect(new URL("/contact", request.url));
  }

  const message = encodeURIComponent("Hi, I found you through AI for U&I and would like to start a conversation.");
  return NextResponse.redirect(`https://wa.me/${number}?text=${message}`);
}
