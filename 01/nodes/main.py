from nodes.graph import graph


def main():

    result = graph.invoke({
        "attempts": 0
    })

    print("\n==============================")
    print("TOPIC")
    print("==============================")

    print(result.get("topic"))

    print("\n==============================")
    print("POST")
    print("==============================")

    print(result.get("final_post"))

    print("\n==============================")
    print("SCORE")
    print("==============================")

    print(result.get("score"))

    print("\n==============================")
    print("TWEET")
    print("==============================")

    print(result.get("tweet_url"))


if __name__ == "__main__":
    main()