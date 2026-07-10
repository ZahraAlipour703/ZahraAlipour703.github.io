import Link from "next/link";

/**
 * 404 page. Rendered for unmatched routes and `notFound()` calls; Next serves
 * it with a 404 status, so crawlers see a proper not-found response.
 */
export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 text-center">
      <h1 className="text-6xl font-bold">404</h1>
      <p className="text-lg">This page could not be found.</p>
      <Link href="/" className="underline underline-offset-4">
        Back to home
      </Link>
    </div>
  );
}
