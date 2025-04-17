# BAYESIAN-JURISPRUDENCE-THE-COURTROOM-GAME-

Let's say we have a case where someone is accused of stealing a wallet in a coffee shop:
Evidence: Security Camera Footage
Scenario: The security camera shows someone in a red jacket taking a wallet. The defendant was wearing a red jacket that day.
To estimate probabilities:
1.	P(evidence|guilty): "If the defendant is guilty, what's the probability they would be wearing a red jacket?"
o	Well, if they committed the crime, they must have been wearing what we saw in the footage: a red jacket
o	So P(evidence|guilty) = 100% or 1.0
2.	P(evidence|innocent): "If the defendant is innocent, what's the probability they would be wearing a red jacket?"
o	This depends on how common red jackets are
o	If we know that about 15% of people in the area wear red jackets, then:
o	P(evidence|innocent) = 15% or 0.15
This creates a likelihood ratio of 1.0/0.15 = 6.67, which means this evidence makes guilt 6.67 times more likely than before we knew about the red jacket.
To make this concrete:
•	If there were 100 people in the coffee shop
•	Originally each person had a 1% chance of being the thief
•	After seeing the footage, someone in a red jacket would have a 6.67% chance of being the thief
The likelihood ratios are then added to the base guilt.  The final sum is then checked against the guilt tolerance for the final verdict.  This approach helps separate what we expect to see if someone is guilty versus what we'd expect if they're innocent, which is the core of Bayesian reasoning in evaluating evidence.
