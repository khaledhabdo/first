"""Unit tests for src/classifier.py."""

import unittest
from src.classifier import classify_statement
from src.models import JobPosting


def make_job(title: str = "Operations Analyst", department: str = "Operations") -> JobPosting:
    return JobPosting(
        board_token="stripe",
        company_name="Stripe",
        job_id=12345,
        job_title=title,
        source_url="https://boards.greenhouse.io/stripe/jobs/12345",
        updated_at="2026-11-14T10:00:00Z",
        first_published="2026-11-01T10:00:00Z",
        location="Remote",
        department=department,
        raw_content="",
    )


class TestClassifier(unittest.TestCase):
    def test_general_software_skills_are_rejected(self) -> None:
        job = make_job("Business Development Representative", "Sales")
        skill_statements = [
            "Experience in Outreach and Salesforce is a plus",
            "Intermediate or stronger Excel or Google Sheets skills, including VLOOKUPs, filters, pivot tables, and data analysis.",
            "Proficiency in using Salesforce, Sales Navigator, and Outreach.",
            "3+ years of experience working day-to-day with marketing automation platforms, CRM platforms, prospect data, and lead management",
            "Familiarity with accounting and financial reconciliation principles",
        ]
        for stmt in skill_statements:
            res = classify_statement(job, stmt)
            self.assertIsNotNone(res, f"Expected match for: {stmt}")
            assert res is not None
            self.assertEqual(res.classification, "REJECTED_FALSE_POSITIVE", f"Failed on: {stmt}")
            self.assertEqual(res.rejection_reason, "GENERAL_SOFTWARE_SKILL", f"Failed on: {stmt}")

    def test_verb_excel_and_idioms_are_rejected(self) -> None:
        job = make_job("Account Executive", "Sales")
        idiom_statements = [
            "We are looking for candidates who excel in a fast-paced environment.",
            "Comfortable presenting to senior leadership and reconciling multiple stakeholder perspectives in writing.",
            "Reporting to the Director of Customer Experience Operations, you will lead global strategy.",
        ]
        for stmt in idiom_statements:
            res = classify_statement(job, stmt)
            self.assertIsNotNone(res, f"Expected match for: {stmt}")
            assert res is not None
            self.assertEqual(res.classification, "REJECTED_FALSE_POSITIVE", f"Failed on: {stmt}")
            self.assertEqual(res.rejection_reason, "VERB_EXCEL_OR_IDIOM", f"Failed on: {stmt}")

    def test_product_pitch_and_engineering_builds_are_rejected(self) -> None:
        pm_job = make_job("Product Manager, Billing", "Product")
        pitch = (
            "Our platform computes hundreds of millions of invoices per billing period, "
            "saving them hours of development time and manual invoicing."
        )
        res_pitch = classify_statement(pm_job, pitch)
        self.assertIsNotNone(res_pitch)
        assert res_pitch is not None
        self.assertEqual(res_pitch.classification, "REJECTED_FALSE_POSITIVE")
        self.assertEqual(res_pitch.rejection_reason, "PRODUCT_PITCH_OR_CUSTOMER_FEATURE")

        eng_job = make_job("Staff Software Engineer, Unified Services Platform", "Engineering")
        eng_stmt = "Design, build, and maintain scalable Apex solutions on the Salesforce platform."
        res_eng = classify_statement(eng_job, eng_stmt)
        self.assertIsNotNone(res_eng)
        assert res_eng is not None
        self.assertEqual(res_eng.classification, "REJECTED_FALSE_POSITIVE")
        self.assertEqual(res_eng.rejection_reason, "ENGINEERING_INFRA_OR_SYSTEMS_BUILD")

    def test_explicit_manual_workflows_are_accepted_without_assuming_buying_intent(self) -> None:
        job = make_job("Legal Entity Controller", "Finance")
        stmt = (
            "Perform and drive monthly and quarterly close activities, including manual journal entries, "
            "balance sheet reconciliations, variance analyses, and analytical reviews, producing internal management reporting"
        )
        res = classify_statement(job, stmt)
        self.assertIsNotNone(res)
        assert res is not None
        self.assertEqual(res.classification, "VALID_SIGNAL")
        self.assertEqual(res.signal_subtype, "DIRECT_MANUAL_EXECUTION")
        self.assertEqual(res.workflow_category, "Data Entry")
        self.assertIn("NO DIRECT BUYING INTENT", res.buying_intent_assessment)
        self.assertEqual(res.source_url, "https://boards.greenhouse.io/stripe/jobs/12345")

    def test_internal_automation_mandate_subtype_is_detected(self) -> None:
        job = make_job("Operations Manager, Strategic Partnerships", "Operations")
        stmt = (
            "Workflow Automation: Utilize modern AI tools and automated workflows to centralize partner data, "
            "streamline pipeline management, and reduce manual reporting overhead."
        )
        res = classify_statement(job, stmt)
        self.assertIsNotNone(res)
        assert res is not None
        self.assertEqual(res.classification, "VALID_SIGNAL")
        self.assertEqual(res.signal_subtype, "INTERNAL_AUTOMATION_MANDATE")
        self.assertEqual(res.workflow_category, "Reporting")
        self.assertIn("NO DIRECT BUYING INTENT", res.buying_intent_assessment)


if __name__ == "__main__":
    unittest.main()
