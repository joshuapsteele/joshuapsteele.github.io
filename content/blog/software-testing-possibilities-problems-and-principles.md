---
title: 'Software Testing: Possibilities, Problems, and Principles'
date: '2022-12-21T21:08:05Z'
author: joshuapsteele
categories:
- software engineering
tags:
- software
- testing
description: An overview of software testing principles and practices, drawing on Khorikov's Unit Testing and Aniche's Effective Software Testing.
url: /software-testing-possibilities-problems-and-principles/
---
Note: Throughout what follows, I am heavily indebted to two books in particular: [Unit Testing: Principles, Practices, and Patterns](https://www.manning.com/books/unit-testing) by [Vladimir Khorikov](https://twitter.com/vkhorikov?lang=en) (Manning Publications, 2020) and [Effective Software Testing: A Developer’s Guide](https://www.manning.com/books/effective-software-testing) by [Mauricio Aniche](https://twitter.com/mauricioaniche) (Manning Publications, 2022). In fact, this overview of software testing should be viewed as a distillation of Khorikov and Aniche.

![Khorikov-UT-HI.png](https://res.craft.do/user/full/032236cd-2bcc-fa12-9dfe-e5564a597e07/doc/836657DD-FF3A-4CE5-8565-F6945FE45D6A/21ECE62D-593E-4825-A549-6312F555D284_2/ZCHd2JrecxcxPA1c35H2wTV0FrAzdktnxui31U1rO00z/Khorikov-UT-HI.png)

![Aniche-HI.png](https://res.craft.do/user/full/032236cd-2bcc-fa12-9dfe-e5564a597e07/doc/836657DD-FF3A-4CE5-8565-F6945FE45D6A/ED1FC92B-C9A0-4CDC-B13D-5AA3940FF3E7_2/FE2KZaydLyYRh1ydJKyDIvx4y3gaQLh82funASwXFqoz/Aniche-HI.png)

---

## Software Testing, Our Field’s Least-Sexy Superpower

Coming into software development from a background in the humanities, automated software testing struck me as a kind of superpower. Until, that is, I had to write my first software test!

So I now think of software testing as software development’s least-sexy superpower.

Sure, tests aren’t very fun or glamorous to write and maintain. But can you imagine if other industries had similar testing powers?

What if your house could test itself and let you know when it needed repairs? What if your body could test itself? What if, every day, you could live your life in the comfort of knowing that you and your belongings were being checked for errors thousands of times? Wouldn’t that be nice? Imagine the security and freedom that such a life-wide testing suite could provide!

![](https://images.unsplash.com/photo-1576267423445-b2e0074d68a4?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxNDIyNzR8MHwxfHNlYXJjaHw3fHxoYXBweSUyMGNvbXB1dGVyfGVufDB8fHx8MTY2NTQ5MjI5MQ&ixlib=rb-1.2.1&q=80&w=1080)

## Possibilities of Software Testing

I don’t know how far away we are from automatic home and health testing, but I do know that automated software testing has the potential to make our lives much better as we develop and sell software.

Sure, software development can get incredibly complicated and frustrating. But what if you had a robust testing suite that:

1. Caught bugs
2. Never “[cried wolf](https://en.wikipedia.org/wiki/The_Boy_Who_Cried_Wolf)” (“to cry wolf” = “to give a false alarm”)
3. Was easy to run, understand, and change

Good tests can help us confidently and quickly develop world-class software that improves our customers’ lives.

It’s not just about catching bugs and passing tests. As Vladimir Khorikov notes in [*Unit Testing: Principles, Practices, and Patterns*](https://learning.oreilly.com/library/view/unit-testing-principles/9781617296277/), **the goal of software testing “is to enable to sustainable growth of the software project.”** The larger and longer a project is around, the more beneficial a good testing suite becomes.

After all, a robust testing suite functions as its own form of **documentation** for your project. A developer should be able to read through the tests and quickly get up to speed with how the production code functions. They can then confidently make changes to the codebase, knowing that (1) they have a decent idea of how things work and (2) that the testing suite will alert them to breaking changes.

And, as we’ll discuss below, [well-designed code is easy to test](https://docs.craft.do/editor/d/032236cd-2bcc-fa12-9dfe-e5564a597e07/836657DD-FF3A-4CE5-8565-F6945FE45D6A/b/C94D92D2-AC78-4BCC-AB6B-5388B77EAF8B#8434D46D-25CD-49D8-83AC-87FE1E45A738)! That is, there’s an important connection between software testing and software **design**. When we run into difficulties writing tests, we should consider improving the design of our production code.

Now, speaking of testing difficulties…

![](https://images.unsplash.com/photo-1516534775068-ba3e7458af70?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxNDIyNzR8MHwxfHNlYXJjaHw1fHxmcnVzdHJhdGVkfGVufDB8fHx8MTY2NTQ5MjMxNw&ixlib=rb-1.2.1&q=80&w=1080)

## Problems with Software Testing

All too often, the reality of software testing falls far short of its potential.

Thanks to the “test early, test often” perspective of [“shift left” testing](https://www.testim.io/blog/shift-left-testing-guide/), most of us software engineers have to write tests. Most of our production code has an ever-increasing **quantity** of test code associated with it. (More on the different [kinds of tests](https://docs.craft.do/editor/d/032236cd-2bcc-fa12-9dfe-e5564a597e07/836657DD-FF3A-4CE5-8565-F6945FE45D6A/b/C94D92D2-AC78-4BCC-AB6B-5388B77EAF8B#AA5E8A29-25DD-4777-80AD-37DF0A172857) below.)

But the **quality** of our testing suites is often lacking.

- We still have to put out fires more often than we’d like
- Our brittle tests “cry wolf” whenever we change anything
- Our tests are difficult to configure, understand, and refactor

In other words, we’re not living up to our testing potential! Or, at least, **I’m** not! Instead, here’s what often happens:

- I make a change to the codebase
- Tests break
- I fix the tests
- My [code quality/coverage analysis tool](https://www.sonarqube.org/) lets me know that I need more code coverage
- I either
- ignore my code coverage tool or
- add some low-quality tests to get the coverage that I need and move my PR forward

This is bad! Don’t be like me! Don’t sacrifice test quality for test quantity.

## How Can <del>Josh</del> We Test Better?

What should we keep in mind when we prepare to write code, when tests break, when our code coverage tool gets mad, etc.?

---

![](https://images.unsplash.com/photo-1598520106830-8c45c2035460?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxNDIyNzR8MHwxfHNlYXJjaHwxfHx3aGl0ZWJvYXJkfGVufDB8fHx8MTY2NTQ5MjE1Ng&ixlib=rb-1.2.1&q=80&w=1080)

## Principles of Software Testing

Lots could and has been said about software testing. But I’d like to do an “80/20 analysis” of software testing and focus on the 20% of principles and mental models that yield 80% of the results.

### What is Software Testing?

Simply put, **software testing is the process of making sure that your software does what you want it to do**.

As we’ll see below, the “process” can be quite complicated and multifaceted. But, before we get there, note that **the prerequisite of software testing is knowing (at least partially) what you want your software to do!**

This is a crucial point to remember, which brings us to our next principle.

### The [Absence of Errors Fallacy](https://www.oodlestechnologies.com/blogs/understanding-absence-of-error-fallacy-in-software-testing/): Passing Tests Don’t Guarantee Good Software

The absence of “errors” doesn’t mean that our software is useful, that it does the right things for our users!

Mauricio Aniche shares the following two quotes/sayings:

- “Coverage of code is easy to measure; coverage of requirements is another matter.”
- “Verification is about having the system right; validation is about having the right system.”

Throughout the iterative process of software testing, we need to ask ourselves **“Do we know what we want our software to do? Should we change the requirements to better meet our users’ needs?”** Only then can we make sure that we are testing for the right behavior.

### Qualities of a Good Test

Khorikov (2020: 67) notes that a good testing suite “provides maximum value with minimum maintenance costs.” But, to achieve this, you need to be able to (1) “recognize a valuable test (and, by extension, a test of low value)” and (2) “write a valuable test.”

To get better at software testing, then, it’s helpful to know what we’re aiming for! Khorikov (2020: 68) lists four qualities of a good test:

- > Protection against regressions
- > Resistance to refactoring
- > Fast feedback
- > Maintainability

Here’s how I would re-phrase that. A good automated software test:

1. Catches bugs (no “false negatives”)
2. Doesn’t “cry wolf” (no “false positives”)
3. Runs quickly
4. Is easy to read and run

OK, so we should just max out each of these four qualities whenever writing tests, right?

Unfortunately, it’s not so simple.

This is because, apart from Maintainability, the other three qualities are in tension with one another. You can only maximize two of the remaining three qualities.

![UnitTesting04fig08_alt.jpeg](https://res.craft.do/user/full/032236cd-2bcc-fa12-9dfe-e5564a597e07/97683B15-BF10-416A-B336-4182179A0E2A_2/bpWRZyrcBDzP71Nk97VopU9hJSQf30X0WDoxASNykDkz/UnitTesting04fig08_alt.jpeg)
(Image source: [Khorikov 2020](https://learning.oreilly.com/library/view/unit-testing-principles/9781617296277/))

And, even then, you can’t completely forget about the last quality you’ve chosen not to prioritize! After all, no one wants a test that (1) doesn’t catch any bugs, (2) is so tightly coupled to the production code that it’s meaningless, or (3) takes forever to run.

![](https://images.unsplash.com/photo-1508935620299-047e0e35fbe3?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxNDIyNzR8MHwxfHNlYXJjaHwxfHxicm9rZW58ZW58MHx8fHwxNjY1NDkyNTcw&ixlib=rb-1.2.1&q=80&w=1080)

### Avoid Brittle Tests: Maximize Resistance to Refactoring

Should we prioritize any particular quality of a good test while we’re building our test suite?

While we need to keep all four qualities in mind throughout the testing process, I agree with Khorikov when he argues for **prioritizing resistance to refactoring**. We need to take special care to avoid producing “brittle” tests that yield false positives (“cry wolf”) whenever we refactor our production code.

Put simply, we need to **test the what, not the how**. (More on this in “[Observable Behavior vs Implementation Details](craftdocs://open?blockId=9811D0C8-FEBE-42CC-BA53-9A767F01549F&spaceId=032236cd-2bcc-fa12-9dfe-e5564a597e07)” below.) Our tests should be as loosely coupled to the implementation details of our production code as possible. Instead, they should focus on testing the observable behavior of our software.

A related concept at this juncture is **“black-box testing vs. white-box testing**“:

- Black-box testing: testing a system’s observable behavior, its specifications and requirements, as if you had no knowledge of its implementation details or inner workings
- White-box testing: testing a system’s implementation details and inner workings

Black-box testing yields better resistance to refactoring. White-box testing might often uncover more bugs than black-box testing, but it often produces brittle tests that are too tightly coupled to implementation details.

Nevertheless, as Khorikov reminds us,

> “even though black-box testing is preferable when *writing tests*, you can still use the white-box method when *analyzing* the tests. *Use code coverage tools to see which code branches are not exercised, but then turn around and test them as if you know nothing about the code’s internal structure.* Such a combination of the white-box and black-box methods works best” (Khorikov 2020).

Why is resistance to refactoring worth prioritizing? Because, as Khorikov notes, unlike protection against regressions and fast feedback, which tend to exist on a spectrum, resistance to refactoring is more of an “all or nothing” aspect of a test.

> “The reason resistance to refactoring is non-negotiable is that whether a test possesses this attribute is mostly a binary choice: the test either has resistance to refactoring or it doesn’t. There are almost no intermediate stages in between. Thus you can’t concede just a little resistance to refactoring: you’ll have to lose it all. On the other hand, the metrics of protection against regressions and fast feedback are more malleable” (Khorikov 2020).

A test is either brittle or it isn’t. And, while the cost of brittle tests is relatively low at the beginning of a project (as long as those tests are catching bugs and running relatively quickly), over time, as a project grows in size and complexity, the costs of brittle tests and their false positives drastically increases.

The main tradeoff we’re left with, then, is between “protection against regressions” and “fast feedback.” And this tradeoff plays itself out in the differences between the main kinds of software tests.

### Kinds of Tests

Fortunately, even though it’s impossible to write a perfect test that maximizes all the qualities of a good test at once, we can and should use different kinds of tests in our software testing suite.

Keep in mind what’s known as “the pesticide paradox”–if you only use one type of test, or you fail to revise and evolve your testing suite, you’ll only catch certain kinds of bugs. To catch new defects in the system, you need to use different kinds of tests and constantly revise your testing suite.

Unfortunately, there’s plenty of debate around the definition of test types, as well as when and how often to use each kind of test. Nevertheless, the following categories are commonly used:

- Unit tests
- Integration tests
- End-to-end tests (AKA System tests)

This framework differentiates tests based on how much code they execute, how quickly they run, how complex they are, and how closely they mimic the behavior of an end user.

#### Unit Tests

Khorikov notes the disagreement on the precise definition of a unit test, but he helpfully isolates the following **three attributes of a unit test** that many definitions share:

> “A unit test is an automated test that

1. > Verifies a small piece of code (also known as a *unit*),
2. > Does it quickly,
3. > And does it in an isolated manner.”

Now, no one really disagrees that unit tests should run **fast** (#2). However, just what counts as a **“unit”** is a matter of some debate. Some people think that a “unit” is a single class or even a single method.

However, as we’ll see below, there are advantages to broadening the definition of “unit” a little bit to mean **“unit of work” or “unit of behavior.”** Doing so helps us to write tests that are loosely coupled to the production code, tightly coupled to business/domain requirements, and therefore resistant to refactoring.

I agree with Khorikov when he advises that

> “Tests shouldn’t verify *units of code*. Rather, they should verify *units of behavior*: something that is meaningful for the problem domain and, ideally, something that a business person can recognize as useful. The number of classes it takes to implement such a unit of behavior is irrelevant. The unit could span across multiple classes or only one class, or even take up just a tiny method.”

Before moving on, we should also note that people disagree on what it means for a unit test to be **“isolated.”**

What’s known as the [**“London School”**](https://medium.com/@adrianbooth/test-driven-development-wars-detroit-vs-london-classicist-vs-mockist-9956c78ae95f) holds that:

- A **unit** is a **single class**
- Each unit should be tested in **isolation from all other units**
- **Test doubles** (mocks, stubs, etc.) should be used for **everything except immutable dependencies** (AKA “values” or “value objects”)

Meanwhile, the [**“Classical School”** (AKA “Detroit School”)](https://medium.com/@adrianbooth/test-driven-development-wars-detroit-vs-london-classicist-vs-mockist-9956c78ae95f) maintains that:

- A **unit** is a **unit of behavior**, no matter how big/small
- Each unit test should run in **isolation from all other unit tests**
- **Test doubles** should **only be used for shared dependencies** (like a database or file system)

It might already be obvious from my comment above about broadening the definition of “unit” to mean “unit of behavior/work,” but I prefer the Classical School’s perspective on testing. It’s easier to produce tests that are resistant to refactoring by following the Classical School’s paradigm.

Despite all the disagreements about unit tests, it’s safe to say that everyone agrees that **unit tests prioritize fast feedback**. They’re quick to write, run, and let you know if you broke something.

#### Integration Tests

Unlike unit tests, **integration tests test more than one unit** **(although not the entire system)**. This means that they tend to take longer to write (and longer to run) than unit tests.

(Note that, because “unit” is used in this definition as well, the arguments about unit tests bleed over into what counts as an integration test! What the “Classical School” calls unit tests, for example, would often be considered integration tests by the “London School.”)

What integration tests give up in terms of fast feedback, they gain in terms of **protection against regressions**. That is, they can catch more bugs.

This is because integration tests exercise more of the codebase than unit tests. They also focus on the interactions between system components, which means that they’re looking for regressions/bugs in areas that are outside of the scope of unit tests.

#### End-to-end or System Tests

Unlike integration tests, end-to-end or system tests **test the entire system**. They take even longer to write and run than integration tests, but they emulate an end-user’s interactions with your system more than any other kind of test.

System tests **maximize protection against regressions** by exercising the entire code base.

Using all three different kinds of tests, then, is key to having a test suite that catches bugs and gives fast feedback.

![UnitTesting04fig12_alt.jpeg](https://res.craft.do/user/full/032236cd-2bcc-fa12-9dfe-e5564a597e07/3554AE46-C4BA-4C5A-B879-2E6B639AA252_2/qH4ihIUx7NKs4kWQNlU3uNEe2Ji1K3CD0cE8Y1svGI8z/UnitTesting04fig12_alt.jpeg)
(Image source: [Khorikov 2020](https://learning.oreilly.com/library/view/unit-testing-principles/9781617296277/))

### The Test Pyramid

Due to the strengths and weaknesses of the three different kinds of tests, the “test pyramid” model suggests that developers should write many unit tests, fewer integration tests, and even fewer end-to-end tests. The width of the pyramid represents the number of tests at each level.

Here is Mauricio Aniche’s version of the Test Pyramid, which adds exploratory manual testing (vs. automated testing) as a top layer:

![EffectiveSoftwareTesting01-08.png](https://res.craft.do/user/full/032236cd-2bcc-fa12-9dfe-e5564a597e07/AFC5E00F-399B-454E-88E9-96DF37822C93_2/a3yCuLMk35hMVojHrgkpkB9dy9tzOB9RlqBjWHdnCZcz/EffectiveSoftwareTesting01-08.png)
(Image source: [Aniche 2022](https://learning.oreilly.com/library/view/effective-software-testing/9781633439931/))

The main reason to be *sparing* in our creation and use of integration and system tests is **time**. Remember, one of the four qualities of a good test is “fast feedback,” and this is definitely a weakness of integration and system tests.

Nevertheless, because they exercise a lot of the codebase (and thereby increase our code coverage), integration and system tests are particularly good at catching bugs. So, if we want our testing suite to be good at “protection against regressions,” we need to include well-thought-out integration and system tests.

### Code Coverage: Good Servant, Bad Master

Code coverage is a measurement of **how much of your production code gets executed by your test code.**

On its own, “code coverage” usually refers to “**line coverage**,” meaning the number of lines of code executed by your tests divided by the total lines of code. (If you’ve got 100 lines of code and your tests execute 90 of them, you’ve got 90% code coverage.)

However, as Aniche (2022) notes, because the complexity of our production code involves more than just the number of lines of code, there are other forms/aspects of code coverage worth considering.

- **Branch coverage** takes into account all the `true` and `false` branches of the program’s logic (coverage of `if(a && b)` must test for both `a && b == true` and `a && b == false`)
- **Condition and branch coverage** builds upon branch coverage to consider each condition that’s a part of a `true` or `false` branch (coverage of `if(a || b)` must test for `a == true`/`b == false`, `a == false`/`b == true`, and `a == false`/`b == false`)
- **Path coverage** is the strictest criteria, considering each and every possible path through the program’s logic (coverage of a program with 10 independent `true/false` conditions would require 2<sup>10</sup> = 1024 test cases)

In a perfect world, we might always want to shoot for 100% path coverage. But, realistically, achieving full path coverage for complicated production code is far too time-consuming to be valuable.

Khorikov lists two main problems with code coverage metrics:

- > You can’t guarantee that the test verifies all the possible outcomes of the system under test.
- > No coverage metric can take into account code paths in external libraries.

Regarding the former problem, the combination of implicit and explicit outcomes of the system under test makes it extremely difficult, if not impossible, to test for them all. And, regarding the latter, code coverage metrics do not take the use of external libraries into consideration.

Does this, then, mean we should not care about code coverage?

No! But, we should keep in mind that, as Khorikov puts it, “coverage metrics are a good negative indicator, but a bad positive one.”

This is related to the “absence-of-errors fallacy” mentioned above. That is, if you have very low code coverage, it’s a sure sign that your testing suite has problems. But the mere fact of a high code coverage percentage does not mean that you have a robust testing suite.

### MC/DC Coverage

Before we move on from code coverage completely, however, I want to mention what’s known as “modified condition / decision coverage” or “MC/DC” as a way to maximize the value of code coverage while minimizing the number of test cases required.

As Aniche (2022) summarizes it, MC/DC

> “looks at combinations of conditions, as path coverage does. However, instead of testing *all* possible combinations, we identify the *important* combinations that need to be tested. MC/DC exercises each of these conditions so that it can, independently of the other conditions, affect the outcome of the entire decision. Every possible condition of each parameter must influence the outcome at least once.”

To achieve MC/DC, you list all possible test cases (those required if you were going for path coverage), before searching for “independence pairs” of test cases where (1) a single condition change (2) independently changes the outcome of the code in question. After finding these independence pairs for all of the conditions, you can reduce the list of test cases down to at least one independence pair for each condition under test.

If we’re just considering binary true/false conditions, then MC/DC requires N + 1 test cases vs path coverage’s 2<sup>N</sup> test cases (Aniche 2022, citing [Chilenski 2001](https://www.google.com/books/edition/An_Investigation_of_Three_Forms_of_the_M/8ibStgAACAAJ?hl=en)).

While MC/DC isn’t a silver bullet to solve all code coverage issues, it’s a great example of applying the “test the what, not the how” testing principle to the topic of code coverage. When deciding which test cases to (not) write, we want to make sure that we’re covering the aspects of our software’s logic that influence it’s observable behavior.

![](https://images.unsplash.com/photo-1503387762-592deb58ef4e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxNDIyNzR8MHwxfHNlYXJjaHw0fHxibHVlcHJpbnR8ZW58MHx8fHwxNjY1NDkyNjMy&ixlib=rb-1.2.1&q=80&w=1080)

### Well-Designed Code is Easy to Test

A deep-dive into software design and architecture far exceeds the scope of this overview of software testing principles. Nevertheless, there’s an important connection between software testing and software design.

Code that is well-designed is easy to test. And code that is difficult to test is often poorly designed.

When testing is integrated into the software development process, then any friction encountered when writing tests should raise questions about the way the production code is structured. Granted, certain difficulties cannot be avoided (sometimes requirements demand behavior that is inherently difficult to test). But there are often ways to improve the design of our production code while also making it easier to test.

### Keep Domain and Infrastructure Code Separate

This is the main design principle that Aniche emphasizes in his chapter on “Designing for testability” in *Effective Software Testing* (2022):

> The *domain* is where the core of the system lies: that is, where all the business rules, logic, entities, services, and similar elements reside. … *Infrastructure* relates to all code that handles an external dependency: for example, pieces of code that handle database queries (in this case, the database is an external dependency) or web service calls or file reads and writes. In our previous examples, all of our data access objects (DAOs) are part of the *infrastructure* code.
> 
> In practice, when domain code and infrastructure code are mixed, the system becomes harder to test. You should separate them as much as possible so the infrastructure does not get in the way of testing.”

Keeping domain code (AKA “business logic”) separate from infrastructure code (AKA “application services layer”) is a key emphasis of the “Hexagonal Architecture” or “Ports and Adapters” pattern.

The business logic at the “center” of your application should only interact with external dependencies by interacting with ports (application services), that interact with adapters, that are themselves coupled to the external dependencies.

![EffectiveSoftwareTesting07-01.png](https://res.craft.do/user/full/032236cd-2bcc-fa12-9dfe-e5564a597e07/163B4C46-ECC3-48AF-82E3-92646C4FBD7B_2/OPm3cFAMHapQQOhihmwAaLVGNND3FpEHM0Fw95If49Ez/EffectiveSoftwareTesting07-01.png)
(Image source: [Aniche 2022](https://learning.oreilly.com/library/view/effective-software-testing/9781633439931/))

This “separation of concerns” approach to software design increases the testability of a system because it allows us to focus our testing efforts, especially at the unit-test level, on the most important part of the system—the domain code—without directly relying on any external dependencies (which could slow our tests down, make them unpredictable, etc.).

Keeping domain code separate from infrastructure code also helps us to avoid writing brittle tests by emphasizing a key principle behind “resistance to refactoring”—observable behavior vs implementation details.

### Observable Behavior vs Implementation Details

At each level of a system, there is an important distinction between ***what* the system is accomplishing (the observable behavior)** and ***how* it accomplishes it (implementation details)**.

At the highest level, *inter-system* communications between applications are observable behaviors, while *intra-system* communication between classes inside an application are implementation details.

![UnitTesting05fig12_alt.jpeg](https://res.craft.do/user/full/032236cd-2bcc-fa12-9dfe-e5564a597e07/doc/836657DD-FF3A-4CE5-8565-F6945FE45D6A/B9F43CB1-DFFA-45E7-9072-18D1BBC56367_2/NBFvJV4sruSIntQaOKcRgfO8WpP7mNWeKI1pmI4eydkz/UnitTesting05fig12_alt.jpeg)
(Image source: [Khorikov 2020](https://learning.oreilly.com/library/view/unit-testing-principles/9781617296277/))

Remember that, as we test each level of the system, in order to avoid writing brittle tests that throw false positives, we need to test the observable behavior, and not the implementation details.

At first glance, it might seem like the distinction is between observable behavior and implementation details is the same as between an applications **public API (application programming interface)** and its **private API**. In languages like C# and Java, this public/private distinction is usually achieved using **access modifiers** (`public`, `private`, `protected`, etc.).

However, although a *well-designed API* has a public API that coincides with its observable behavior and a private API that coincides with its implementation details, it’s very easy and common for an application to **“leak” its implementation details into its public API** by making those implementation details inappropriately observable.

Khorikov highlights the differences here as follows:

> “For a piece of code to be part of the system’s observable behavior, it has to do one of the following things:

- > Expose an operation that helps the client achieve one of its goals. An *operation* is a method that performs a calculation or incurs a side effect or both.
- > Expose a state that helps the client achieve on of its goals. *State* is the current condition of the system.

> Any code that does neither of these two things is an implementation detail.”

Whenever an application “leaks” its implementation details into its public API, it makes it easy for developers to write brittle tests. As Khorikov observes, “by making all implementation details private, you leave your tests no choice other than to verify the code’s observable behavior, which automatically improves their resistance to refactoring.”

### Four Types of Code: Complexity/Significance vs Number of Dependencies

In addition to the distinction between observable behavior and implementation details, there’s an important framework to keep in mind when determining how to test each part of our software system.

![UnitTesting07fig01_alt.jpeg](https://res.craft.do/user/full/032236cd-2bcc-fa12-9dfe-e5564a597e07/doc/836657DD-FF3A-4CE5-8565-F6945FE45D6A/FEB14714-FF80-4C38-A57F-7F190BFF4A40_2/zxxZxZZDo7qDyNjq1Sya4VF9CAK4SnL5jPb7pMnyNmMz/UnitTesting07fig01_alt.jpeg)
(Image source: [Khorikov 2020](https://learning.oreilly.com/library/view/unit-testing-principles/9781617296277/))

Khorikov lists the following four types of production code:

- > *Domain model and algorithms (top left)*—Complex code is often part of the domain model but not in 100% of all cases. You might have a complex algorithm that’s not directly related to the problem domain.
- > *Trivial code (bottom left)*—Examples of such code in C# are parameter-less constructors and one-line properties: they have few (if any) collaborators and exhibit little complexity or domain significance.
- > *Controllers (bottom right)*—This code doesn’t do complex or business-critical work by itself but coordinates the work of other components like domain classes and external applications.
- > *Overcomplicated code (top right)*—Such code scores highly on both metrics: it has a lot of collaborators, and it’s also complex or important. An example here are *fat controllers* (controllers that don’t delegate complex work anywhere and do everything themselves).

Although trivial code is difficult, if not impossible, to avoid, well-designed software systems avoid “overcomplicated code” by making sure that code is either complex/significant OR it works with a number of dependencies, but not both at the same time.

Put differently, the more complicated the code, or the more significant for the domain layer, the fewer collaborators it should have.

Why? Because, at least from a testing perspective, collaborators are expensive and time-consuming to test. Restricting interaction with collaborators to “controllers” in the application services / infrastructure layer of our application allows us to be strategic in our use of **test doubles and integration tests for the controllers**, while spending more of our valuable time writing **unit tests for our domain code and complex algorithms**.

<figure>![UnitTesting08fig01_alt.jpeg](https://res.craft.do/user/full/032236cd-2bcc-fa12-9dfe-e5564a597e07/doc/836657DD-FF3A-4CE5-8565-F6945FE45D6A/D2685F77-D498-4959-9B7D-6FF2DEEAC26A_2/IP8Scjkvxo8Egqj2Fz8ly0vviNmuKTxCKtz97Fyfz5sz/UnitTesting08fig01_alt.jpeg)<figcaption>UnitTesting08fig01\_alt.jpeg</figcaption></figure>
(Image source: [Khorikov 2020](https://learning.oreilly.com/library/view/unit-testing-principles/9781617296277/))

If the classes in our domain code depend only on each other, they should be relatively easy and quick to unit test. Then, after checking as many edge cases as possible in our unit tests, we can judiciously test the happy paths and all other edge cases in our integration tests of the controllers in the application service layer.

Nevertheless, even if we do all of this properly, we still need to reckon with collaborators and dependencies at some point, ideally without making our testing suite prohibitively expensive and time-consuming to run! This brings us to the important topic of test doubles.

![](https://images.unsplash.com/photo-1620889276134-ea33a1084664?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxNDIyNzR8MHwxfHNlYXJjaHw3NHx8bWFubmVxdWlufGVufDB8fHx8MTY2NTQ5MjczMQ&ixlib=rb-1.2.1&q=80&w=1080)

### Test Doubles: Mocks vs Stubs

Test doubles (think “stunt doubles”) mimic the behavior of dependencies. There are various kinds of test doubles. Aniche (2022) lists five, for example:

- Dummies: passed to the class under test but never used
- Fakes: use simplified implementations of the classes they mimic
- Stubs: provide hard-coded answers to queries (no simplified implementation like fakes)
- Mocks: provide hard-coded answers to queries, recording the interactions that can then be asserted afterward
- Spies: wrap around a real dependency object (not like a mock), recording the interactions (like a mock)

However, Khorikov (2020) helpfully simplifies this list down to just two kinds of test doubles:

- Mocks (including both mocks and spies)
- Stubs (including dummies, fakes, and stubs)

What’s the difference between the two? Here’s Khorikov again:

- > Mocks help to emulate and examine *outcoming* interactions. These interactions are calls the SUT \[System Under Test\] makes to its dependencies to change their state.
- > Stubs help to emulate *incoming* interactions. These interactions are calls the SUT makes to its dependencies to get input data

Notice two important things. First, mocks both *emulate* and *examine*, while stubs only *emulate*. Second, mocks mimic interactions that result in *side effects* or changed state, while stubs mimc interactions that *retrieve information*. This touches on another important principle: command query separation.

### Command Query Separation

According to command query separation (CQS), “every method should be either a command or a query, but not both” (Khorikov 2020).

- Commands: produce side effects, but do not return a value
- Queries: return a value, but do not produce side effects

Another way of summarizing this principle is that “asking a question should not change the answer” (Khorikov 2020).

Note that, in terms of CQS, mocks mimic commands while stubs mimic queries.

![Image.tiff](https://res.craft.do/user/full/032236cd-2bcc-fa12-9dfe-e5564a597e07/doc/836657DD-FF3A-4CE5-8565-F6945FE45D6A/9A23E848-9BAF-4318-8874-FA36C3D793F6_2/x5OUyH6SgUYVQnLrLvyE0Bya9z3mvCQcJrtuH90Ndxsz/Image.tiff)
(Image source: [Khorikov 2020](https://learning.oreilly.com/library/view/unit-testing-principles/9781617296277/))

### When to Use Mocks and Stubs

A corollary of what we’ve just discussed is that we should **never assert (verify) interactions with stubs in our tests**. Doing so is unnecessary if our tests are correctly focusing on observable behavior, because stubs should only ever emulate steps on the way to our SUT (system under test) producing observable output.

A corollary of what we previously discussed about complexity/significance vs number of collaborators means that **we should not have to use test doubles in our unit tests of domain code (and complex algorithms), but should rather save mocks and stubs for our integration tests of controllers and application services code**.

Put differently: save test doubles for the outside “edges” of your system, where you need to verify interactions with dependencies that you don’t have control over.

When unit testing domain code classes at the “center” of your system, the only direct dependencies should be upon other domain code classes. And, since we’ve already discussed the benefit of expanding our definition of “unit” beyond “class” to include “unit of behavior/work,” **we should use real versions of these “in-process” dependencies in our unit tests, instead of replacing them with mocks or stubs**.

And, even when writing integration tests for application service code, when interactions with “out-of-process” dependencies are inescapable, **we should only replace unmanaged out-of-process dependencies with test doubles. Whenever possible, we should use real instances of managed out-of-process dependencies (such as a database) in our integration tests, rather than replacing these with mocks or stubs**.

Finally, when replacing unmanaged dependencies with test doubles, we should do so by creating (and then mocking or stubbing) an adapter layer that stands between our application and the third-party dependency. In other words, even when mocking a dependency you don’t control, you should “only mock types that you own” (Khorikov 2020). This doesn’t mean that you should mock managed dependencies like your database (see above)! But it does add in a helpful buffer between your application and its unmanaged dependencies.

![](https://images.unsplash.com/photo-1471958680802-1345a694ba6d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxNDIyNzR8MHwxfHNlYXJjaHw2fHxyb2FkfGVufDB8fHx8MTY2NTQ5MjQ3Mw&ixlib=rb-1.2.1&q=80&w=1080)

## Conclusion

Much more could be (and has been) said about software testing! If I had more time, I would discuss the following. But I recommend that curious readers do their own research on:

- [Parameterized testing](https://www.baeldung.com/parameterized-tests-junit-5), which can help save time and space when you’ve got a bunch of test cases you need to cover for a single method
- [Property-based testing](https://medium.com/criteo-engineering/introduction-to-property-based-testing-f5236229d237), which leverages software to create and handle test cases given pre-defined “properties” or parameters that should be followed when generating possible inputs for your tests
- [Mutation testing](https://en.wikipedia.org/wiki/Mutation_testing), which makes dynamic changes (“mutants”!) to your production code, and then sees whether or not those changes cause a test to fail (if, say, changing an `if (A)` to `if (!A)` causes a test to fail, then you’ve “killed” the mutant; if changing the logic of your program doesn’t cause any tests to fail, then the mutant has “survived”)

…Not to mention doing your own research on testing libraries and frameworks in your favorite language(s)! (In Java world, that includes [JUnit](https://junit.org/junit5/), [Mockito](https://site.mockito.org/), [jqwik](https://jqwik.net/), [AssertJ](https://assertj.github.io/doc/), [Pitest](https://pitest.org/), etc.)

Nevertheless, I hope that this overview of software testing possibilities, problems, and principles helps you to write better tests and develop better software! If you have anything to add or correct, please do leave a comment. Or reach out to me (Twitter [@joshuapsteele](https://twitter.com/joshuapsteele), GitHub [jsteelepfpt](https://github.com/jsteelepfpt), LinkedIn [joshuapsteele](https://www.linkedin.com/in/joshuapsteele/)).

---

![](https://images.unsplash.com/photo-1600431521340-491eca880813?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxNDIyNzR8MHwxfHNlYXJjaHw2fHxsaWJyYXJ5fGVufDB8fHx8MTY2NTQ5MjQzNA&ixlib=rb-1.2.1&q=80&w=1080)

## Recommended Resources on Software Testing

- Test Case Checklist in [*Code Complete*](https://learning.oreilly.com/library/view/code-complete-2nd/0735619670/), 2nd edition by Steve McConnell (Microsoft 2004:532)
- [*Effective Software Testing: A Developer’s Guide*](https://learning.oreilly.com/library/view/effective-software-testing/9781633439931/) by Mauricio Aniche (Manning, 2022)
- [*Full Stack Testing: A Practical Guide for Delivering High Quality Software*](https://learning.oreilly.com/library/view/full-stack-testing/9781098108120/) by Gayathri Mohan (O’Reilly, 2022)
- [*Unit Testing Principles, Practices, and Patterns*](https://learning.oreilly.com/library/view/unit-testing-principles/9781617296277/) by Vladimir Khorikov (Manning, 2020)
- “[Topic 41: Test to Code](https://learning.oreilly.com/library/view/the-pragmatic-programmer/9780135956977/f_0065.xhtml)” and “[Topic 42: Property-Based Testing](https://learning.oreilly.com/library/view/the-pragmatic-programmer/9780135956977/f_0066.xhtml)” in [*The Pragmatic Programmer: Your Journey to Mastery*](https://learning.oreilly.com/library/view/the-pragmatic-programmer/9780135956977/) by David Thomas and Andrew Hunt (2nd Edition; Addison-Wesley Professional, 2019)
- “[Testing Strategies in a Microservice Architecture](https://martinfowler.com/articles/microservice-testing/)” by Toby Clemson (Slide Deck)
- “[What Is Software Testing? And Why Is It So Hard?](https://profinit.eu/wp-content/uploads/2016/03/HardSwTesting.pdf)” by James A. Whittaker (IEEE Software, January 2000:70–79)
