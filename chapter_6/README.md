# Chapter 6 -

The hallway chatter about the Train Logistics&trade; application is increasing, and you can feel the deadline for
having your integration test setup approaching. Having achieved the basics in chapter 5, enabling you to test with the
Tickets API, you realize there is no reason to have the Tickets API with your integration tests. The packaging in
chapter 5 feels strange, and it would make more sense to separate the two. No mono-repo today.

You decide to split the Tickets API into a separate repository, which is also what you will do with the Train
Logistics&trade; application. Finally, you can have your integration tests in its own repository as well, and you can
have a clean separation of concerns.

## Setup

Once again, the layout of the project has changed. The `tickets_api` is now gone and the `integration_tests` package is
the sole survivor. This repository is from here on out solely concerned with orchestrating integration tests while our
application software and dependencies lives elsewhere.

Same as always, create a new virtual environment for this chapter. Ensure the new environment is activated in
your active terminal.

Install dependencies and the application itself.

```
pip install ".[dev]"
```

## Task 1: Where did the Tickets API go?

The Tickets API is now in its own repository, and you can find it [here](https://github.com/equinor/tickets-api). The
repository contains the same code as before and there is not much different apart from modularization. There is however
one major change we have made which will allow us to run our integration tests still.

In the previous chapter, the custom container for the Tickets API was built using the Testcontainers `DockerImage`
class. Now that we have moved the context away from our local repository we must either fetch the remote repository or
build the docker image elsewhere. The [tickets-api repository](https://github.com/equinor/tickets-api) has a published
package which is created automatically on new releases. This is done
by [this workflow](https://github.com/equinor/tickets-api/blob/main/.github/workflows/publish_docker_image.yml).

The workflow publishes the package to the GitHub Container Registry. This works well, particularly open source as we are
now, but you can also use it for private repositories or decide to host your own container registry.

Your task is to update the fixture for our custom Tickets API container to use the remotely published docker image on
GitHub Container Registry instead of building it locally. Once you have done so, ensure all the tests pass by running
`pytest -s`.

## Task 2: Run the integration tests in a remote repository