from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import proof_scraping_lab


class FakeResponse:
    def __init__(self, text: str, status_code: int = 200) -> None:
        self.text = text
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"http {self.status_code}")


class FakeSession:
    def __init__(self, pages: dict[str, str]) -> None:
        self.pages = pages

    def get(self, url: str, timeout: int) -> FakeResponse:
        if url not in self.pages:
            raise RuntimeError(f"missing page for {url}")
        return FakeResponse(self.pages[url])


class ProofScrapingLabTests(unittest.TestCase):
    def test_parse_proof_page_extracts_pair_links_and_blocks(self) -> None:
        url = "https://teorth.github.io/equational_theories/implications/show_proof.html?pair=1,2"
        body = """
        <html><body>
        <h1>Equation1[x = y] implies Equation2[x = z]</h1>
        <a href="show_proof.html?pair=3,4">Equation3[a = b] implies Equation4[c = d]</a>
        <a href="https://github.com/teorth/equational_theories/blob/main/Facts.lean">Facts lemma</a>
        <pre>construction := shift operator</pre>
        <code>counterexample family</code>
        <table><tr><td>not a small table</td></tr></table>
        </body></html>
        """
        parsed = proof_scraping_lab.parse_proof_page(body, url, 1, 2)
        self.assertEqual(parsed["pair"], [1, 2])
        self.assertEqual(parsed["pair_links"][0]["pair"], [3, 4])
        self.assertEqual(parsed["fact_links"][0]["name"], "Facts lemma")
        self.assertIn("shift operator", parsed["pre_blocks"][0])
        self.assertIn("counterexample family", parsed["code_blocks"][0])
        self.assertIn("not a small table", parsed["table_blocks"][0])

    def test_crawl_pairs_uses_cache_on_second_fetch(self) -> None:
        first_url = "https://teorth.github.io/equational_theories/implications/show_proof.html?pair=1,2"
        html = "<html><body><h1>Pair</h1></body></html>"
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_dir = Path(tmp_dir)
            session = FakeSession({first_url: html})
            rows_first, manifest_first = proof_scraping_lab.crawl_pairs(
                seed_pairs=[(1, 2)],
                recursive=False,
                limit=0,
                session=session,
                timeout_s=30,
                retries=1,
                sleep_s=0.0,
                cache_dir=cache_dir,
                refresh_cache=False,
            )
            self.assertEqual(rows_first[0]["fetched_from"], "network")
            self.assertEqual(manifest_first["ok_count"], 1)

            session_empty = FakeSession({})
            rows_second, _ = proof_scraping_lab.crawl_pairs(
                seed_pairs=[(1, 2)],
                recursive=False,
                limit=0,
                session=session_empty,
                timeout_s=30,
                retries=1,
                sleep_s=0.0,
                cache_dir=cache_dir,
                refresh_cache=False,
            )
            self.assertEqual(rows_second[0]["fetched_from"], "cache")

    def test_recursive_crawl_discovers_child_pair_links(self) -> None:
        root = "https://teorth.github.io/equational_theories/implications/show_proof.html?pair=1,2"
        child = "https://teorth.github.io/equational_theories/implications/show_proof.html?pair=3,4"
        with tempfile.TemporaryDirectory() as tmp_dir:
            session = FakeSession(
                {
                    root: '<html><body><h1>Root</h1><a href="show_proof.html?pair=3,4">child</a></body></html>',
                    child: '<html><body><h1>Child</h1></body></html>',
                }
            )
            rows, manifest = proof_scraping_lab.crawl_pairs(
                seed_pairs=[(1, 2)],
                recursive=True,
                limit=0,
                session=session,
                timeout_s=30,
                retries=1,
                sleep_s=0.0,
                cache_dir=Path(tmp_dir),
                refresh_cache=False,
            )
            self.assertEqual(len(rows), 2)
            self.assertEqual(manifest["discovered_edge_count"], 1)
            self.assertEqual(manifest["discovered_edges"][0]["to"], [3, 4])


if __name__ == "__main__":
    unittest.main()