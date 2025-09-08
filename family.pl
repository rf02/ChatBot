% Facts
:- dynamic male/1, female/1, father/2, mother/2.

male(john).
female(mary).

% Dynamic rules 
:- dynamic parent/2, child/2, grandparent/2, grandfather/2, grandmother/2.
:- dynamic sibling/2, brother/2, sister/2.
:- dynamic son/2, daughter/2.
:- dynamic uncle/2, aunt/2.
:- dynamic parents/3.
:- dynamic ancestor/2.
:- dynamic related/2.

% Rules
parent(X, Y) :- father(X, Y).
parent(X, Y) :- mother(X, Y).

child(Y, X) :- parent(X, Y).
grandparent(X, Y) :- parent(X, Z), parent(Z, Y).
grandfather(X, Y) :- male(X), grandparent(X, Y).
grandmother(X, Y) :- female(X), grandparent(X, Y).

sibling(X, Y) :- parent(Z, X), parent(Z, Y), X \= Y.
brother(X, Y) :- male(X), sibling(X, Y).
sister(X, Y) :- female(X), sibling(X, Y).

son(X, Y) :- male(X), child(X, Y).
daughter(X, Y) :- female(X), child(X, Y).

uncle(X, Y) :- male(X), sibling(X, Z), parent(Z, Y).
aunt(X, Y) :- female(X), sibling(X, Z), parent(Z, Y).

parents(X, Y, Z) :- father(Y, X), mother(Z, X).

ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).

% General relatives
related(X, Y) :- parent(X, Y).
related(X, Y) :- parent(Y, X).
related(X, Y) :- sibling(X, Y).
related(X, Y) :- sibling(Y, X).
related(X, Y) :- ancestor(X, Y).
related(X, Y) :- ancestor(Y, X).

