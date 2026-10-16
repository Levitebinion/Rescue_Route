from src.fifo import allocate_fifo
from src.greedy import allocate_greedy
from src.metrics import summarize
from src.report import build_report
from tests.helpers import make_donation, make_recipient, make_volunteer


def _report_for(donations, recipients, volunteers):
    fifo = allocate_fifo(donations, recipients, volunteers)
    greedy = allocate_greedy(donations, recipients, volunteers)
    return build_report(
        donations, fifo, greedy,
        summarize(donations, recipients, volunteers, fifo),
        summarize(donations, recipients, volunteers, greedy),
    )


def test_report_explains_each_donation_the_strategies_disagree_on():
    donations = [make_donation("relaxed", shelf_life=200, quantity=5),
                 make_donation("urgent", shelf_life=10, quantity=5)]
    report = _report_for(donations, [make_recipient(capacity=5)], [make_volunteer()])

    assert "### urgent: assigned under greedy only" in report
    assert "### relaxed: assigned under FIFO only" in report
    assert "less remaining shelf life" in report          # the "why" is in there
    assert "trade-off" in report


def test_report_lists_both_processing_orders():
    donations = [make_donation("relaxed", shelf_life=200), make_donation("urgent", shelf_life=10)]
    report = _report_for(donations, [make_recipient()], [make_volunteer()])
    assert "FIFO (arrival order): relaxed, urgent" in report
    assert "Greedy (urgency-first): urgent, relaxed" in report


def test_report_says_so_when_strategies_agree():
    donations = [make_donation("only")]
    report = _report_for(donations, [make_recipient()], [make_volunteer()])
    assert "identical outcomes" in report
    assert "### " not in report.split("## Donations handled differently")[1].split("## Summary")[0]