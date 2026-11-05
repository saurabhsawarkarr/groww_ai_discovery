import sqlite3
import json
import re

def enrich_record(rec_id, raw_text, quote, current_stage, current_beh, current_fric):
    """Derive rich, sensible, context-accurate behavioral attributes from the quote and raw text."""
    text = (quote or "") + " " + (raw_text or "")
    lower = text.lower()

    # --- 1. PRECISE JOURNEY STAGE DETERMINATION ---
    stage = current_stage or "unknown"
    
    # Positive / Continuing signals
    if any(k in lower for k in ["completed 1 year", "completed 12 month", "18 consecutive", "completed exactly 12", "disciplined investing habit", "consecutive month"]):
        stage = "continuing"
    elif "instead of stopping" in lower or "stepped up my monthly contribution" in lower or "discipline" in lower:
        stage = "continuing"
    elif any(k in lower for k in ["started my first", "1st sip", "first sip", "first 3 month", "first 2 month", "2 months ago", "3 months ago", "started 1000", "started with just rs 500"]):
        stage = "newly_started"
    elif any(k in lower for k in ["thinking of pausing", "thinking of stopping", "reconsidering", "should i stop", "does it still make sense"]):
        stage = "considering_change"
    elif any(k in lower for k in ["paused for 2 months", "paused automatically", "pause this sip", "want to pause"]):
        stage = "paused"
    elif any(k in lower for k in ["cancelled my sip", "stopped that sip", "stopped my equity", "had to stop my", "stopped my monthly", "redeem my 5 month", "stopped all 3"]):
        stage = "stopped"
    elif any(k in lower for k in ["how to start", "first time mutual fund buyer question", "is it good to invest in", "planning to"]):
        stage = "before_starting"

    # --- 2. REPORTED BEHAVIOUR ---
    beh = "Monitoring mutual fund SIP investment and performance"
    
    # Stepping up / Continuation
    if "stepped up" in lower or "step up" in lower or "instead of stopping" in lower:
        beh = "Maintained SIP discipline and stepped up monthly contribution amount"
    elif "completed 1 year" in lower or "completed 12 month" in lower or "completed exactly 12" in lower or "18 consecutive" in lower:
        beh = "Consistently executed recurring monthly SIP instalments for 12+ months"
    elif "daughter was born" in lower or "child" in lower:
        beh = "Established recurring long-term monthly SIP anchored to child future goal"
    
    # Portfolio Cleanup & Overlap
    elif "hold the exact same" in lower or "overlapping" in lower or "clean up" in lower or "7 different funds" in lower or "6 different sips" in lower:
        beh = "Reviewing multi-fund portfolio to eliminate overlapping stock holdings"
    elif "redirected the money into uti" in lower or "index fund" in lower and "stopped" in lower:
        beh = "Pruned active fund SIPs to consolidate contributions into low-cost index fund"
    elif "direct plan" in lower and ("regular" in lower or "stopped that sip" in lower):
        beh = "Terminated third-party regular plan SIP to switch to Groww direct plan"
    elif "switched from zerodha coin" in lower or "soa" in lower:
        beh = "Migrated mutual fund investments from Demat broker to Groww SOA format"
    
    # Stopping / Liquidations with specific motives
    elif "wedding" in lower or "jewell" in lower or "hall booking" in lower:
        beh = "Liquidated SIP investments to finance major life event (wedding expenses)"
    elif "laptop broke" in lower or "emergency fund" in lower:
        beh = "Redeemed fund units prematurely due to lack of liquid emergency reserves"
    elif "emi starts" in lower or "home loan" in lower:
        beh = "Halted recurring SIP instalments to prioritize upcoming loan EMI commitments"
    elif "covid crash" in lower and "cancelled" in lower:
        beh = "Panic-liquidated fund units during broad market crash"
    elif "bounce charge" in lower or "ecs bounce" in lower or "450" in lower:
        beh = "Terminated autopay mandate to avoid bank ECS debit bounce penalties"
    elif "negative" in lower and ("stop" in lower or "cancel" in lower):
        beh = "Stopped recurring SIP mandate following early-tenure paper losses"
    elif "gold" in lower and "stopped" in lower:
        beh = "Reallocated monthly savings from equity SIP into Sovereign Gold Bonds (SGB)"
    elif "lumpsum" in lower and "bonus" in lower:
        beh = "Deployed annual performance bonus as a lump-sum mutual fund investment"
        
    # Technical & Mandate Behaviours
    elif "enach to upi" in lower or "change autopay" in lower:
        beh = "Attempting to migrate autopay mandate authorization from eNACH to UPI"
    elif "npci" in lower or ("mandate failed" in lower or "failed" in lower and "autopay" in lower):
        beh = "Troubleshooting failed autopay debit following partner bank gateway downtime"
    elif "bank still deduc" in lower or "2 days before" in lower:
        beh = "Attempted pre-instalment SIP cancellation but encountered bank debit lag"
    elif "friday" in lower and ("tuesday" in lower or "allocated" in lower or "debited" in lower):
        beh = "Tracking weekend settlement clearance and NAV unit allotment timing"
    elif "deduction date" in lower and ("salary" in lower or "10th" in lower or "5th" in lower):
        beh = "Adjusted SIP deduction date to align with monthly salary credit schedule"
    elif "wallet" in lower and ("remove" in lower or "withdraw" in lower or "100" in lower):
        beh = "Attempting wallet balance withdrawal to registered primary bank account"
    elif "xirr" in lower and ("total return" in lower or "10%" in lower or "18%" in lower or "+12%" in lower):
        beh = "Comparing annualized XIRR calculations against absolute portfolio cash returns"
    elif "idcw" in lower and "growth" in lower:
        beh = "Rectifying accidental IDCW (Dividend) plan selection to switch to Growth plan"
    elif "exit load" in lower or "redeeming" in lower and "shocked" in lower:
        beh = "Inquiring about unexpected exit load deduction upon early unit redemption"
    elif "stamp duty" in lower:
        beh = "Auditing transaction fee ledger for statutory stamp duty deductions"
    elif "daily sip" in lower:
        beh = "Evaluating high-frequency daily micro-SIP vs monthly investing routine"
    elif "bi-weekly" in lower or "weekly sip" in lower:
        beh = "Inquiring about return variance between weekly vs monthly SIP schedules"
    elif "pay now" in lower:
        beh = "Executing manual ad-hoc UPI payment ahead of scheduled autopay deduction"
    elif "cas statement" in lower or "mfcentral" in lower:
        beh = "Reconciling Consolidated Account Statement (CAS) via MFCentral portal"
    elif stage == "stopped":
        beh = "Terminated recurring mutual fund SIP instalments"
    elif stage == "paused":
        beh = "Paused recurring SIP contributions temporarily"

    # --- 3. FRICTION / CONCERN ---
    fric = current_fric
    if "wallet" in lower and "100" in lower:
        fric = "Groww wallet minimum withdrawal threshold constraint (Rs 100 limit)"
    elif "exit load" in lower:
        fric = "Surprise 1% exit load charge on early redemption within 12 months"
    elif "stamp duty" in lower:
        fric = "Lack of clarity regarding statutory 0.005% stamp duty deductions"
    elif "npci" in lower or "bank otp" in lower or "enach to upi" in lower:
        fric = "Bank gateway authentication failures and inflexible mandate modification"
    elif "ecs bounce" in lower or "bounce charge" in lower:
        fric = "Fear of severe bank ECS bounce fees (Rs 400-500) during cash crunch"
    elif "negative" in lower or "in red" in lower or "-8%" in lower or "-2.5%" in lower:
        fric = "Acute loss aversion panic from early negative returns in months 1-3"
    elif "overlap" in lower or "7 different funds" in lower or "6 different sips" in lower:
        fric = "Severe portfolio overlap (70%+ common stocks) and decision paralysis"
    elif "xirr" in lower and ("distort" in lower or "fluctuate" in lower or "explain" in lower):
        fric = "Difficulty interpreting volatile annualized XIRR vs absolute return %"
    elif "friday" in lower and ("tuesday" in lower or "4 days" in lower or "delay" in lower):
        fric = "Anxiety caused by multi-day NAV allotment delays over weekends (T+2/T+3)"
    elif "bank still deduc" in lower or "cancelled my sip" in lower:
        fric = "Bank mandate cancellation lag (bank debits despite app cancellation)"
    elif "idcw" in lower:
        fric = "Accidental enrollment in dividend payout plan due to confusing UI toggle"
    elif "laptop broke" in lower or "emergency" in lower:
        fric = "Forced premature liquidation due to lack of liquid emergency buffer"
    elif "deduction date" in lower and "salary" in lower:
        fric = "Cash flow timing mismatch between salary credit and SIP debit date"
    elif "covid crash" in lower:
        fric = "Emotional panic selling during macro market drawdowns"

    # --- 4. TRIGGER / SITUATION ---
    trig = None
    if "salary" in lower or "bonus" in lower:
        trig = "Salary credit / bonus liquidity timing"
    elif "daughter was born" in lower or "wedding" in lower or "hall booking" in lower:
        trig = "Major life milestone event (childbirth / marriage)"
    elif "laptop broke" in lower or "emergency" in lower:
        trig = "Sudden unexpected emergency expense"
    elif "finfluencer" in lower or "youtube" in lower:
        trig = "Social media / finfluencer investment recommendation"
    elif "negative" in lower or "market crash" in lower or "red" in lower:
        trig = "Market correction / short-term negative portfolio return"
    elif "bank mandate failed" in lower or "otp" in lower or "npci" in lower:
        trig = "Upstream banking partner API failure"
    elif "completed 1 year" in lower or "12 months" in lower:
        trig = "Reaching 1-year investment milestone"
    elif "tax" in lower or "stcg" in lower:
        trig = "Budget tax announcement (LTCG/STCG changes)"

    # --- 5. OBSERVED WORKAROUND ---
    workaround = None
    if "instead of stopping" in lower and "stepped up" in lower:
        workaround = "Stepped up contribution amount during market correction to average down cost"
    elif "direct plan" in lower:
        workaround = "Switched to Direct mutual fund plan on Groww to eliminate distributor commissions"
    elif "mfcentral" in lower or "cas" in lower:
        workaround = "Used external MFCentral portal to verify consolidated portfolio holdings"
    elif "10th" in lower and "5th" in lower:
        workaround = "Rescheduled autopay debit date to 10th to guarantee post-salary clearance"
    elif "pay now" in lower:
        workaround = "Executed manual instant UPI payment rather than waiting for autopay batch"
    elif "index fund" in lower and "stopped" in lower:
        workaround = "Consolidated multiple overlapping funds into a single low-cost Nifty 50 Index fund"
    elif "soa" in lower:
        workaround = "Transferred holdings to SOA format to eliminate Demat maintenance fees"

    # --- 6. REPORTED OUTCOME ---
    outcome = None
    if stage == "continuing":
        outcome = "Successfully maintained continuous disciplined investing habit"
    elif stage == "stopped":
        outcome = "SIP mandate terminated; contributions halted"
    elif stage == "paused":
        outcome = "SIP temporarily placed on hold pending cash flow recovery"
    elif stage == "considering_change":
        outcome = "User actively evaluating fund alternatives or portfolio restructuring"
    elif stage == "newly_started":
        outcome = "Active in first 90 days; observing daily return trajectory"

    return {
        "journey_stage": stage,
        "reported_behaviour": beh,
        "friction_or_concern": fric,
        "trigger_or_situation": trig,
        "workaround": workaround,
        "reported_outcome": outcome,
    }

print("Loaded enricher module successfully.")
