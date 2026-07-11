import type { NavItem } from "@/types";

export const site = {
  name: "AIforU&I",
  advisorName: "Ramya Amballa",
  tagline: "[Site Tagline Placeholder]",
  description:
    "[Site Meta Description Placeholder — independent advisory positioning across AI governance, digital governance, cyber governance, technology risk and third-party governance.]",
  url: "https://www.aiforuandi.com",
  locale: "en_US",
  twitter: "@aiforuandi",
} as const;

export const primaryNav: NavItem[] = [
  { label: "Home", href: "/" },
  { label: "Selected Advisory Engagements", href: "/selected-advisory-engagements" },
  { label: "Advisory Services", href: "/advisory-services" },
  { label: "Governance Domains", href: "/governance-domains" },
  { label: "Insights", href: "/insights" },
  { label: "Resources", href: "/resources" },
  { label: "About Ramya", href: "/about" },
  { label: "Contact", href: "/contact" },
];

export const footerNav: { title: string; items: NavItem[] }[] = [
  {
    title: "Advisory",
    items: [
      { label: "Selected Advisory Engagements", href: "/selected-advisory-engagements" },
      { label: "Advisory Services", href: "/advisory-services" },
      { label: "Governance Domains", href: "/governance-domains" },
    ],
  },
  {
    title: "Perspective",
    items: [
      { label: "Insights", href: "/insights" },
      { label: "Resources", href: "/resources" },
    ],
  },
  {
    title: "Firm",
    items: [
      { label: "About Ramya", href: "/about" },
      { label: "Contact", href: "/contact" },
    ],
  },
];

export const primaryCta: NavItem = {
  label: "Selected Advisory Engagements",
  href: "/selected-advisory-engagements",
};

export const secondaryCta: NavItem = {
  label: "Start a Conversation",
  href: "/contact",
};
