cmake_minimum_required(VERSION 2.8)

project(solver)

add_library(solver solver.c)

install(TARGETS solver DESTINATION /usr/lib)