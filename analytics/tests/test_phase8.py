from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class BrowserInstrumentationTests(unittest.TestCase):
    def test_browser_events_are_same_origin_fixed_and_privacy_limited(self) -> None:
        script = (ROOT / "assets" / "lionpath-app.js").read_text(encoding="utf-8")
        self.assertIn("fetch('/api/analytics/event'", script)
        self.assertIn("body: JSON.stringify(payload)", script)
        self.assertIn("credentials: 'same-origin'", script)
        self.assertIn("keepalive: true", script)
        instrumentation = script[
            script.index("const ANALYTICS_SECTIONS"):script.index("let nativeCompassModel")
        ]
        for forbidden in ("planName", "planQuestions", "nativeCompassModel.state", "userAgent"):
            self.assertNotIn(forbidden, instrumentation)

    def test_expected_feature_events_are_wired(self) -> None:
        script = (ROOT / "assets" / "lionpath-app.js").read_text(encoding="utf-8")
        for event in (
            "section_view", "career_assessment_start", "career_assessment_complete",
            "course_explorer_open", "plan_open", "plan_print", "plan_pdf_download",
            "evidence_open", "evidence_pdf_download", "ai_coach_open", "schoolai_launch",
            "voice_coach_launch", "counseling_link_open",
        ):
            self.assertIn(f"'{event}'", script)

    def test_privacy_copy_describes_first_party_events(self) -> None:
        page = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("anonymous visits and fixed feature-use events", page)
        self.assertIn("assessment answers, plan contents, names, and AI conversations are not sent", page)


if __name__ == "__main__":
    unittest.main()
