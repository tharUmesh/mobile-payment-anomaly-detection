#!/usr/bin/env python3
import sys

def run_reducer():
    current_account = None
    transactions = []

    # Read the sorted Key-Value pairs from standard input
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            # Split the line into Key (account) and Value (tx_data)
            account, tx_data = line.split('\t', 1)
            step, tx_type, amount, newbalance, dest = tx_data.split(',')
            
            # Rebuild the transaction dictionary
            tx = {
                'step': int(step),
                'type': tx_type,
                'amount': float(amount),
                'newbalance': float(newbalance),
                'dest': dest
            }
        except ValueError:
            continue

        # If we are still reading transactions for the same account, group them
        if current_account == account:
            transactions.append(tx)
        else:
            # If the account changes, process the previous account's transactions
            if current_account:
                detect_anomalies(current_account, transactions)
            
            # Reset for the new account
            current_account = account
            transactions = [tx]

    # Don't forget to process the very last account in the stream
    if current_account:
        detect_anomalies(current_account, transactions)

def detect_anomalies(account, transactions):
    # Sort chronologically by 'step'. 
    # If steps are identical, sort by 'newbalance' descending to ensure 0.0 is last.
    transactions.sort(key=lambda x: (x['step'], -x['newbalance']))
    
    # --- STRATEGY 1: Transfer-then-Cash-Out Pivot ---
    for i in range(len(transactions) - 1):
        tx1 = transactions[i]
        tx2 = transactions[i+1]
        
        if tx1['type'] == 'TRANSFER' and tx2['type'] == 'CASH_OUT':
            # Threshold: Happens within 2 steps, and initial transfer is large
            if (tx2['step'] - tx1['step'] <= 2) and tx1['amount'] >= 200000:
                print(f"{account}\tANOMALY: Transfer-then-Cash-Out Pivot (Amount: {tx1['amount']})")
                return # Alert triggered, exit early for this account

    # --- STRATEGY 2: High-Velocity Account Depletion ---
    if len(transactions) >= 3:
        # Threshold: 3+ transactions dropping the balance to exactly 0.0 in a short time
        if transactions[-1]['newbalance'] == 0.0:
            step_range = transactions[-1]['step'] - transactions[0]['step']
            if step_range <= 1:
                 print(f"{account}\tANOMALY: High-Velocity Depletion (Drained to 0 in {step_range} steps)")
                 return

    # --- STRATEGY 3: Scattering Pattern ---
    # Count unique destination accounts for outgoing money
    dests = set([tx['dest'] for tx in transactions if tx['type'] in ('TRANSFER', 'PAYMENT')])
    
    # Threshold: Sending money to 5+ distinct accounts within 3 steps
    if len(dests) >= 5:
         step_range = transactions[-1]['step'] - transactions[0]['step']
         if step_range <= 3:
              print(f"{account}\tANOMALY: Scattering Pattern ({len(dests)} distinct destinations)")

if __name__ == "__main__":
    run_reducer()