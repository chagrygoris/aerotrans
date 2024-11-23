def create_rectangles(flights):
    rectangles_html = []
    for flight in flights:
        flight_html = f"""
        <div class="flight-rectangle">
            <h3>Flight from {flight['from_city']} to {flight['to_city']}</h3>
            <p>Date: {flight['date']}</p>
            <p>Price: {flight['price']}</p>
            <p>Airline: {flight['airline']}</p>
            <p>Flight Time: {flight['flight_time']}</p>
        </div>
        """
        rectangles_html.append(flight_html)
    return "".join(rectangles_html)
