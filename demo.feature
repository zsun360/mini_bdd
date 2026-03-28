Feature: Calculator core flow

Scenario: add two numbers
  Given I have numbers 2 and 3
  When I add them
  Then the result should be 5

Scenario: subtract with And and But
  Given I have numbers 10 and 4
  And I am in calc mode
  When I subtract them
  Then the result should be 6
  But the result should not be 5