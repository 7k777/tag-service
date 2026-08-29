const API_ORIGIN = "https://wallet.newkis.cc";

function withSecurityHeaders(response) {
  const headers = new Headers(response.headers);
  headers.set("X-Content-Type-Options", "nosniff");
  headers.set("Referrer-Policy", "no-referrer");
  headers.set("X-Frame-Options", "DENY");
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname.startsWith("/api/")) {
      const upstreamPath = url.pathname.slice(4);
      const allowed = /^\/(login|register|health|tags(?:\/.*)?)$/.test(upstreamPath);
      if (!allowed) return new Response("Not found", { status: 404 });

      const upstream = new URL(API_ORIGIN);
      upstream.pathname = "/tags-api" + upstreamPath;
      upstream.search = url.search;

      const headers = new Headers(request.headers);
      headers.delete("host");
      headers.delete("origin");
      headers.delete("referer");
      for (const name of [...headers.keys()]) {
        if (name.toLowerCase().startsWith("cf-")) headers.delete(name);
      }

      const init = {
        method: request.method,
        headers,
        redirect: "manual"
      };
      if (request.method !== "GET" && request.method !== "HEAD") {
        init.body = request.body;
      }

      try {
        const response = await fetch(upstream, init);
        const safe = withSecurityHeaders(response);
        safe.headers.set("Cache-Control", "no-store");
        return safe;
      } catch {
        return Response.json(
          { detail: "标签服务器暂时无法连接，请稍后再试" },
          { status: 502, headers: { "Cache-Control": "no-store" } }
        );
      }
    }

    return withSecurityHeaders(await env.ASSETS.fetch(request));
  }
};
