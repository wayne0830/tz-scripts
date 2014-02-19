#!/usr/bin/python
#coding=utf8

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

def color(s, color=WHITE):
    return "\033[0;%dm%s\033[0m" % (30+color, str(s))

def red(s):
    return color(s, RED)

def green(s):
    return color(s, GREEN)

def yellow(s):
    return color(s, YELLOW)

def blue(s):
    return color(s, BLUE)

def magenta(s):
    return color(s, MAGENTA)

def cyan(s):
    return color(s, CYAN)
