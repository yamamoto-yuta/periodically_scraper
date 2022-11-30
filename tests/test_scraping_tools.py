from http import HTTPStatus

from periodically_scraper.shared.scraping_tools import get_html


class TestGetResponse:
    def test_http_status_200(self, mocker):
        mock = mocker.Mock()
        mock.status_code = HTTPStatus.OK
        mocker.patch('requests.get').return_value = mock

        _, status_code = get_html("")

        assert status_code == HTTPStatus.OK

    def test_http_status_404(self, mocker):
        mock = mocker.Mock()
        mock.status_code = HTTPStatus.NOT_FOUND
        mocker.patch('requests.get').return_value = mock

        _, status_code = get_html("")

        assert status_code == HTTPStatus.NOT_FOUND

    def test_http_status_others(self, mocker):
        mock = mocker.Mock()
        mock.status_code = 999
        mocker.patch('requests.get').return_value = mock

        _, status_code = get_html("")

        assert status_code == 999

    def test_http_status_all_500(self, mocker):
        mock = mocker.Mock()
        mock.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        mocker.patch('requests.get').return_value = mock

        _, status_code = get_html("")

        assert status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    def test_unstable_connection(self, mocker):
        mock_200 = mocker.Mock()
        mock_200.status_code = HTTPStatus.OK
        mock_500 = mocker.Mock()
        mock_500.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        mocker.patch('requests.get').side_effect = [mock_500, mock_500, mock_200]

        _, status_code = get_html("")

        assert status_code == HTTPStatus.OK
