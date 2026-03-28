from registry import given, when, then


@given(r"^I have numbers (?P<a>\d+) and (?P<b>\d+)$")
def have_numbers(ctx, a, b):
    ctx.a = int(a)
    ctx.b = int(b)


@given(r"^I am in calc mode$")
def calc_mode(ctx):
    ctx.mode = "calc"


@when(r"^I add them$")
def add(ctx):
    ctx.result = ctx.a + ctx.b


@when(r"^I subtract them$")
def subtract(ctx):
    ctx.result = ctx.a - ctx.b


@then(r"^the result should be (?P<expected>\d+)$")
def result_is(ctx, expected):
    assert ctx.result == int(expected), f"expected {expected}, got {ctx.result}"


@then(r"^the result should not be (?P<unexpected>\d+)$")
def result_is_not(ctx, unexpected):
    assert ctx.result != int(unexpected), f"did not expect {unexpected}"