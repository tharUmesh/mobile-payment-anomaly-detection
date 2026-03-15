#!/usr/bin/env python3
import sys

def run_reducer():
    current_account = None
    transactions = []

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            account, tx_data = line.split('\t', 1)
            # Unpack the 8 fields we mapped
            step, tx_type, amount, oldbalanceOrg, newbalanceOrig, dest, oldbalanceDest, newbalanceDest = tx_data.split(',')
            
            tx = {
                'step': int(step),
                'type': tx_type,
                'amount': float(amount),
                'oldbalanceOrg': float(oldbalanceOrg),
                'newbalanceOrig': float(newbalanceOrig),
                'dest': dest,
                'oldbalanceDest': float(oldbalanceDest),
                'newbalanceDest': float(newbalanceDest)
            }
        except ValueError:
            continue

        if current_account == account:
            transactions.append(tx)
        else:
            if current_account:
                detect_anomalies(current_account, transactions)
            current_account = account
            transactions = [tx]

    if current_account:
        detect_anomalies(current_account, transactions)

def detect_anomalies(account, transactions):
    # Sort chronologically, then by newbalance descending
    transactions.sort(key=lambda x: (x['step'], -x['newbalanceOrig']))
    
    for tx in transactions:
        # --- STRATEGY 1: Exact Account Drain (PaySim Signature) ---
        # The fraudster transfers/cashes out the exact starting balance, leaving 0.
        if tx['type'] in ('TRANSFER', 'CASH_OUT') and tx['amount'] > 0:
            if abs(tx['amount'] - tx['oldbalanceOrg']) < 0.01 and tx['newbalanceOrig'] == 0.0:
                print(f"{account}\tANOMALY: Complete Account Drain (Amount: {tx['amount']})")
                return # Alert triggered, exit early for this account
        
        # --- STRATEGY 2: Blackhole Transfer Destination ---
        # A massive transfer occurs, but the destination account records 0 balance change.
        if tx['type'] == 'TRANSFER' and tx['amount'] > 100000:
            if tx['oldbalanceDest'] == 0.0 and tx['newbalanceDest'] == 0.0:
                print(f"{account}\tANOMALY: Blackhole Destination (Amount: {tx['amount']})")
                return

    # --- STRATEGY 3: High-Velocity Depletion ---
    if len(transactions) >= 3:
        if transactions[-1]['newbalanceOrig'] == 0.0:
            step_range = transactions[-1]['step'] - transactions[0]['step']
            if step_range <= 1:
                 print(f"{account}\tANOMALY: High-Velocity Depletion (Drained to 0 in {step_range} steps)")
                 return

    # --- STRATEGY 4: Scattering Pattern ---
    dests = set([tx['dest'] for tx in transactions if tx['type'] in ('TRANSFER', 'PAYMENT')])
    if len(dests) >= 5:
         step_range = transactions[-1]['step'] - transactions[0]['step']
         if step_range <= 3:
              print(f"{account}\tANOMALY: Scattering Pattern ({len(dests)} distinct destinations)")

if __name__ == "__main__":
    run_reducer()