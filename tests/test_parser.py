import json

from asynctest import Mock

from search_service.parser import WikiParser


def test_parse_response():
    kafka_producer = Mock()
    client_session = Mock()
    parser = WikiParser(kafka_producer, client_session)
    with open('tests/io/response.json') as f:
        response = json.load(f)
    result = parser.parse_response(response)
    expected_result = [
        {'title': 'Nelson Mandela', 'url': 'https://en.wikipedia.org/wiki/Nelson_Mandela'},
        {'title': 'Winnie Madikizela-Mandela', 'url': 'https://en.wikipedia.org/wiki/Winnie_Madikizela-Mandela'},
        {'title': 'Mandela Barnes', 'url': 'https://en.wikipedia.org/wiki/Mandela_Barnes'},
        {'title': 'Makaziwe Mandela', 'url': 'https://en.wikipedia.org/wiki/Makaziwe_Mandela'},
        {'title': 'Zindzi Mandela', 'url': 'https://en.wikipedia.org/wiki/Zindzi_Mandela'},
        {'title': 'Death of Nelson Mandela', 'url': 'https://en.wikipedia.org/wiki/Death_of_Nelson_Mandela'},
        {'title': 'Mandla Mandela', 'url': 'https://en.wikipedia.org/wiki/Mandla_Mandela'},
        {'title': 'Zoleka Mandela', 'url': 'https://en.wikipedia.org/wiki/Zoleka_Mandela'},
        {'title': 'Mandela Effect (album)', 'url': 'https://en.wikipedia.org/wiki/Mandela_Effect_(album)'},
        {'title': 'The Mandela Effect (film)', 'url': 'https://en.wikipedia.org/wiki/The_Mandela_Effect_(film)'}
    ]
    assert result == expected_result

    result = parser.parse_response({})
    assert result == []
