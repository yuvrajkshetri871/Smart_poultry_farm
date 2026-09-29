import sympy as sp


def calculate_farm_projection(birds, eggs_per_bird, feed_per_bird, feed_price):
    birds = sp.Float(birds)
    eggs_per_bird = sp.Float(eggs_per_bird)
    feed_per_bird = sp.Float(feed_per_bird)
    feed_price = sp.Float(feed_price)

    total_eggs = birds * eggs_per_bird
    total_feed = birds * feed_per_bird
    feed_cost = total_feed * feed_price

    return {
        "total_eggs": round(float(total_eggs), 2),
        "total_feed": round(float(total_feed), 2),
        "feed_cost": round(float(feed_cost), 2)
    }