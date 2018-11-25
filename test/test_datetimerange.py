# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import unicode_literals

from copy import deepcopy
from datetime import date, datetime, timedelta

import pytest
import pytz
from datetimerange import DateTimeRange
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


TIMEZONE = "+0900"
START_DATETIME_TEXT = "2015-03-22T10:00:00" + TIMEZONE
END_DATETIME_TEXT = "2015-03-22T10:10:00" + TIMEZONE

TEST_START_DATETIME = parse(START_DATETIME_TEXT)
TEST_END_DATETIME = parse(END_DATETIME_TEXT)
ISO_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def setup_module(module):
    import locale

    locale.setlocale(locale.LC_ALL, ("C", "ascii"))


@pytest.fixture
def datetimerange_normal():
    value = DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME)
    value.start_time_format = ISO_TIME_FORMAT
    value.end_time_format = ISO_TIME_FORMAT

    return value


@pytest.fixture
def datetimerange_inversion():
    value = DateTimeRange(TEST_END_DATETIME, TEST_START_DATETIME)
    value.start_time_format = ISO_TIME_FORMAT
    value.end_time_format = ISO_TIME_FORMAT

    return value


@pytest.fixture
def datetimerange_null():
    value = DateTimeRange(None, None)
    value.time_format = None
    value.end_time_format = None

    return value


@pytest.fixture
def datetimerange_null_start():
    value = DateTimeRange(None, TEST_END_DATETIME)
    value.time_format = None
    value.end_time_format = ISO_TIME_FORMAT

    return value


class Test_DateTimeRange_repr(object):
    @pytest.mark.parametrize(
        ["start", "start_format", "end", "end_format", "separator", "is_output_elapse", "expected"],
        [
            [
                TEST_START_DATETIME,
                ISO_TIME_FORMAT,
                TEST_END_DATETIME,
                ISO_TIME_FORMAT,
                " - ",
                False,
                "2015-03-22T10:00:00+0900 - 2015-03-22T10:10:00+0900",
            ],
            [
                "2015-03-22T09:00:00+0900",
                ISO_TIME_FORMAT,
                "2015-03-22T10:10:00+0900",
                ISO_TIME_FORMAT,
                " - ",
                False,
                "2015-03-22T09:00:00+0900 - 2015-03-22T10:10:00+0900",
            ],
            [
                "2015-03-22T09:00:00",
                ISO_TIME_FORMAT,
                "2015-03-22T10:10:00",
                ISO_TIME_FORMAT,
                " - ",
                False,
                "2015-03-22T09:00:00 - 2015-03-22T10:10:00",
            ],
            [
                TEST_START_DATETIME,
                ISO_TIME_FORMAT,
                TEST_END_DATETIME,
                ISO_TIME_FORMAT,
                " - ",
                True,
                "2015-03-22T10:00:00+0900 - 2015-03-22T10:10:00+0900 (0:10:00)",
            ],
            [
                TEST_END_DATETIME,
                ISO_TIME_FORMAT,
                TEST_START_DATETIME,
                ISO_TIME_FORMAT,
                " - ",
                True,
                "2015-03-22T10:10:00+0900 - 2015-03-22T10:00:00+0900 (-1 day, 23:50:00)",
            ],
            [
                TEST_START_DATETIME,
                "%Y%m%d%H%M%S",
                TEST_END_DATETIME,
                "%Y/%m/%d %H:%M:%S%z",
                " to ",
                False,
                "20150322100000 to 2015/03/22 10:10:00+0900",
            ],
            [
                None,
                ISO_TIME_FORMAT,
                TEST_END_DATETIME,
                ISO_TIME_FORMAT,
                " - ",
                False,
                "NaT - 2015-03-22T10:10:00+0900",
            ],
            [
                TEST_START_DATETIME,
                ISO_TIME_FORMAT,
                None,
                ISO_TIME_FORMAT,
                " - ",
                False,
                "2015-03-22T10:00:00+0900 - NaT",
            ],
            [
                "2015-03-22",
                "%Y-%m-%d",
                "2015-04-22",
                "%Y-%m-%d",
                " - ",
                False,
                "2015-03-22 - 2015-04-22",
            ],
            [
                date(2015, 3, 22),
                "%Y-%m-%d",
                date(2015, 4, 22),
                "%Y-%m-%d",
                " - ",
                False,
                "2015-03-22 - 2015-04-22",
            ],
            ["01:23:45", "%H:%M:%S", "11:23:45", "%H:%M:%S", " - ", False, "01:23:45 - 11:23:45"],
            [None, ISO_TIME_FORMAT, None, ISO_TIME_FORMAT, " - ", False, "NaT - NaT"],
        ],
    )
    def test_normal(
        self, start, start_format, end, end_format, separator, is_output_elapse, expected
    ):
        dtr = DateTimeRange(start, end, start_format, end_format)
        dtr.separator = separator
        dtr.is_output_elapse = is_output_elapse
        assert str(dtr) == expected

    @pytest.mark.parametrize(
        ["start", "start_format", "end", "end_format", "expected"],
        [
            [
                "2015-03-08T00:00:00-0400",
                ISO_TIME_FORMAT,
                "2015-03-08T12:00:00-0400",
                ISO_TIME_FORMAT,
                "2015-03-08T00:00:00-0400 - 2015-03-08T12:00:00-0300",
            ],
            [
                "2015-11-01T00:00:00-0400",
                ISO_TIME_FORMAT,
                "2015-11-01T12:00:00-0400",
                ISO_TIME_FORMAT,
                "2015-11-01T00:00:00-0300 - 2015-11-01T12:00:00-0400",
            ],
        ],
    )
    def test_daylight_saving_time(self, start, start_format, end, end_format, expected):
        dtr = DateTimeRange(start, end, start_format, end_format)
        assert str(dtr) == expected

    @pytest.mark.parametrize(
        ["start", "start_format", "end", "end_format", "separator", "is_output_elapse", "expected"],
        [
            [
                TEST_START_DATETIME,
                None,
                TEST_END_DATETIME,
                ISO_TIME_FORMAT,
                " - ",
                False,
                TypeError,
            ],
            [
                TEST_START_DATETIME,
                ISO_TIME_FORMAT,
                TEST_END_DATETIME,
                None,
                " - ",
                False,
                TypeError,
            ],
            [
                TEST_START_DATETIME,
                ISO_TIME_FORMAT,
                TEST_END_DATETIME,
                ISO_TIME_FORMAT,
                None,
                False,
                AttributeError,
            ],
        ],
    )
    def test_exception(
        self, start, start_format, end, end_format, separator, is_output_elapse, expected
    ):
        dtr = DateTimeRange(start, end, start_format, end_format)
        dtr.separator = separator
        dtr.is_output_elapse = is_output_elapse
        with pytest.raises(expected):
            str(dtr)


class Test_DateTimeRange_eq(object):
    @pytest.mark.parametrize(
        ["lhs", "rhs", "expected"],
        [
            [DateTimeRange(None, None), DateTimeRange(None, None), True],
            [
                DateTimeRange("2015-03-22T10:00:00+0900", "2015-03-22T10:10:00+0900"),
                DateTimeRange("2015-03-22T10:00:00+0900", "2015-03-22T10:10:00+0900"),
                True,
            ],
            [
                DateTimeRange("2015-03-22T10:00:00", "2015-03-22T10:10:00"),
                DateTimeRange("2015-03-22T10:00:00", "2015-03-22T10:10:00"),
                True,
            ],
            [
                DateTimeRange("2015-03-22T10:00:00+0900", "2015-03-22T10:10:00+0900"),
                DateTimeRange("2015-03-22T10:00:00+0900", "2015-03-22T10:20:00+0900"),
                False,
            ],
            [
                DateTimeRange("2015-03-22T10:00:00+0900", "2015-03-22T10:10:00+0900"),
                DateTimeRange("2015-03-22T10:02:00+0900", "2015-03-22T10:10:00+0900"),
                False,
            ],
            [
                DateTimeRange("2015-03-22T10:00:00+0900", "2015-03-22T10:10:00+0900"),
                DateTimeRange("2015-03-22T11:00:00+0900", "2015-03-22T12:10:00+0900"),
                False,
            ],
            [DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME), None, False],
            [None, DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME), False],
        ],
    )
    def test_normal(self, lhs, rhs, expected):
        assert (lhs == rhs) == expected


class Test_DateTimeRange_neq(object):
    @pytest.mark.parametrize(
        ["lhs", "rhs", "expected"],
        [
            [DateTimeRange(None, None), DateTimeRange(None, None), False],
            [
                DateTimeRange("2015-03-22T10:00:00+0900", "2015-03-22T10:10:00+0900"),
                DateTimeRange("2015-03-22T10:00:00+0900", "2015-03-22T10:10:00+0900"),
                False,
            ],
            [
                DateTimeRange("2015-03-22T10:00:00", "2015-03-22T10:10:00"),
                DateTimeRange("2015-03-22T10:00:00", "2015-03-22T10:10:00"),
                False,
            ],
            [
                DateTimeRange("2015-03-22T10:00:00+0900", "2015-03-22T10:10:00+0900"),
                DateTimeRange("2015-03-22T10:00:00+0900", "2015-03-22T10:20:00+0900"),
                True,
            ],
            [
                DateTimeRange("2015-03-22T10:00:00+0900", "2015-03-22T10:10:00+0900"),
                DateTimeRange("2015-03-22T10:02:00+0900", "2015-03-22T10:10:00+0900"),
                True,
            ],
            [
                DateTimeRange("2015-03-22T10:00:00+0900", "2015-03-22T10:10:00+0900"),
                DateTimeRange("2015-03-22T11:00:00+0900", "2015-03-22T12:10:00+0900"),
                True,
            ],
            [DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME), None, True],
            [None, DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME), True],
        ],
    )
    def test_normal(self, lhs, rhs, expected):
        assert (lhs != rhs) == expected


class Test_DateTimeRange_add(object):
    @pytest.mark.parametrize(
        ["value", "add_value", "expected"],
        [
            [
                DateTimeRange("2015-03-22T10:00:00+0900", "2015-03-22T10:10:00+0900"),
                timedelta(seconds=10 * 60),
                DateTimeRange("2015-03-22T10:10:00+0900", "2015-03-22T10:20:00+0900"),
            ],
            [
                DateTimeRange("2015-03-22T10:00:00", "2015-03-22T10:10:00"),
                timedelta(seconds=-10 * 60),
                DateTimeRange("2015-03-22T09:50:00", "2015-03-22T10:00:00"),
            ],
        ],
    )
    def test_normal(self, value, add_value, expected):
        new_datetimerange = value + add_value

        assert new_datetimerange == expected

    @pytest.mark.parametrize(
        ["value", "expected"],
        [["2015-03-22T10:10:00+0900", TypeError], [1, TypeError], [None, TypeError]],
    )
    def test_exception(self, datetimerange_normal, value, expected):
        with pytest.raises(TypeError):
            datetimerange_normal + value

    def test_null(self, datetimerange_null):
        with pytest.raises(TypeError):
            datetimerange_null + timedelta(seconds=10 * 60)


class Test_DateTimeRange_iadd(object):
    def test_normal(self):
        value = DateTimeRange("2015-03-22T10:00:00+0900", "2015-03-22T10:10:00+0900")
        expected = DateTimeRange("2015-03-22T10:10:00+0900", "2015-03-22T10:20:00+0900")

        value += timedelta(seconds=10 * 60)
        assert value == expected

    @pytest.mark.parametrize(
        ["value", "expected"],
        [["2015-03-22T10:10:00+0900", TypeError], [1, TypeError], [None, TypeError]],
    )
    def test_exception(self, datetimerange_normal, value, expected):
        with pytest.raises(TypeError):
            datetimerange_normal += value

    def test_null(self, datetimerange_null):
        with pytest.raises(TypeError):
            datetimerange_null += timedelta(seconds=10 * 60)


class Test_DateTimeRange_sub(object):
    def test_normal(self):
        value = DateTimeRange("2015-03-22T10:10:00+0900", "2015-03-22T10:20:00+0900")
        expected = DateTimeRange("2015-03-22T10:00:00+0900", "2015-03-22T10:10:00+0900")

        new_datetimerange = value - timedelta(seconds=10 * 60)
        assert new_datetimerange == expected

    @pytest.mark.parametrize(
        ["value", "expected"],
        [["2015-03-22T10:10:00+0900", TypeError], [1, TypeError], [None, TypeError]],
    )
    def test_exception(self, datetimerange_normal, value, expected):
        with pytest.raises(TypeError):
            datetimerange_normal - value

    def test_null(self, datetimerange_null):
        with pytest.raises(TypeError):
            datetimerange_null - timedelta(seconds=10 * 60)


class Test_DateTimeRange_isub(object):
    def test_normal(self):
        value = DateTimeRange("2015-03-22T10:10:00+0900", "2015-03-22T10:20:00+0900")
        expected = DateTimeRange("2015-03-22T10:00:00+0900", "2015-03-22T10:10:00+0900")

        value -= timedelta(seconds=10 * 60)
        assert value == expected

    @pytest.mark.parametrize(
        ["value", "expected"],
        [["2015-03-22T10:10:00+0900", TypeError], [1, TypeError], [None, TypeError]],
    )
    def test_exception(self, datetimerange_normal, value, expected):
        with pytest.raises(TypeError):
            datetimerange_normal -= value

    def test_null(self, datetimerange_null):
        with pytest.raises(TypeError):
            datetimerange_null -= timedelta(seconds=10 * 60)


class Test_DateTimeRange_contains(object):
    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            [START_DATETIME_TEXT, True],
            [END_DATETIME_TEXT, True],
            [TEST_START_DATETIME, True],
            [TEST_END_DATETIME, True],
            [
                DateTimeRange("2015-03-22 10:05:00" + TIMEZONE, "2015-03-22 10:06:00" + TIMEZONE),
                True,
            ],
            [
                DateTimeRange("2015-03-22 10:10:01" + TIMEZONE, "2015-03-22 10:11:01" + TIMEZONE),
                False,
            ],
            ["2015-03-22 09:59:59" + TIMEZONE, False],
            ["2015-03-22 10:10:01" + TIMEZONE, False],
        ],
    )
    def test_normal(self, datetimerange_normal, value, expected):
        assert (value in datetimerange_normal) == expected

    @pytest.mark.parametrize(
        ["value", "expected"], [[None, TypeError], [False, TypeError], [20140513221937, TypeError]]
    )
    def test_exception(self, datetimerange_normal, value, expected):
        with pytest.raises(expected):
            value in datetimerange_normal

    @pytest.mark.parametrize(
        ["value", "expected"],
        [[TEST_START_DATETIME, TypeError], ["aaa", TypeError], [None, TypeError]],
    )
    def test_null_start(self, datetimerange_null_start, value, expected):
        with pytest.raises(expected):
            value in datetimerange_null_start


class Test_DateTimeRange_timedelta(object):
    def test_normal(self, datetimerange_normal):
        assert datetimerange_normal.timedelta == timedelta(seconds=10 * 60)

    @pytest.mark.parametrize(
        ["start", "end", "expected"],
        [
            [
                "2015-03-08T00:00:00-0400",
                "2015-03-08T12:00:00-0400",
                timedelta(0, 39600),  # 11 hours
            ],
            [
                "2015-11-01T00:00:00-0400",
                "2015-11-01T12:00:00-0400",
                timedelta(0, 46800),  # 13 hours
            ],
        ],
    )
    def test_daylight_saving_time(self, start, end, expected):
        dtr = DateTimeRange(start, end)
        assert dtr.timedelta == expected

    def test_inversion(self, datetimerange_inversion):
        assert datetimerange_inversion.timedelta == timedelta(-1, 85800)

    def test_null(self, datetimerange_null):
        with pytest.raises(TypeError):
            datetimerange_null.timedelta

    def test_exception(self, datetimerange_null_start):
        with pytest.raises(TypeError):
            datetimerange_null_start.timedelta


class Test_DateTimeRange_is_set(object):
    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            [DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME), True],
            [DateTimeRange(TEST_END_DATETIME, TEST_START_DATETIME), True],
            [DateTimeRange(TEST_START_DATETIME, None), False],
            [DateTimeRange(None, TEST_START_DATETIME), False],
            [DateTimeRange(None, None), False],
        ],
    )
    def test_normal(self, value, expected):
        assert value.is_set() == expected


class Test_DateTimeRange_validate_time_inversion(object):
    @pytest.mark.parametrize(
        ["value"],
        [
            [DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME)],
            [DateTimeRange(TEST_START_DATETIME, TEST_START_DATETIME)],
        ],
    )
    def test_normal(self, value):
        value.validate_time_inversion()

    def test_inversion(self, datetimerange_inversion):
        with pytest.raises(ValueError):
            datetimerange_inversion.validate_time_inversion()

    @pytest.mark.parametrize(
        ["value"],
        [
            [DateTimeRange(None, None)],
            [DateTimeRange(None, TEST_END_DATETIME)],
            [DateTimeRange(TEST_START_DATETIME, None)],
        ],
    )
    def test_exception(self, value):
        with pytest.raises(TypeError):
            value.validate_time_inversion()


class Test_DateTimeRange_is_valid_timerange(object):
    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            [DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME), True],
            [DateTimeRange(TEST_END_DATETIME, TEST_START_DATETIME), False],
            [DateTimeRange(TEST_START_DATETIME, None), False],
            [DateTimeRange(None, TEST_START_DATETIME), False],
            [DateTimeRange(None, None), False],
        ],
    )
    def test_normal(self, value, expected):
        assert value.is_valid_timerange() == expected


class Test_DateTimeRange_range(object):
    @pytest.mark.parametrize(
        ["value", "step", "expected"],
        [
            [
                DateTimeRange(datetime(2015, 3, 22, 0, 0, 0), datetime(2015, 3, 22, 0, 1, 0)),
                timedelta(seconds=20),
                [
                    datetime(2015, 3, 22, 0, 0, 0),
                    datetime(2015, 3, 22, 0, 0, 20),
                    datetime(2015, 3, 22, 0, 0, 40),
                    datetime(2015, 3, 22, 0, 1, 00),
                ],
            ],
            [
                DateTimeRange(datetime(2015, 3, 22, 0, 0, 0), datetime(2015, 3, 23, 0, 0, 0)),
                relativedelta(hours=+6),
                [
                    datetime(2015, 3, 22, 0, 0, 0),
                    datetime(2015, 3, 22, 6, 0, 0),
                    datetime(2015, 3, 22, 12, 0, 0),
                    datetime(2015, 3, 22, 18, 0, 0),
                    datetime(2015, 3, 23, 0, 0, 0),
                ],
            ],
            [
                DateTimeRange(datetime(2015, 3, 22, 0, 0, 0), datetime(2015, 3, 23, 0, 0, 0)),
                relativedelta(months=+6),
                [datetime(2015, 3, 22, 0, 0, 0)],
            ],
            [
                DateTimeRange("2015-01-01T00:00:00+0900", "2016-01-01T00:00:00+0900"),
                relativedelta(months=+4),
                [
                    parse("2015-01-01T00:00:00+0900"),
                    parse("2015-05-01T00:00:00+0900"),
                    parse("2015-09-01T00:00:00+0900"),
                    parse("2016-01-01T00:00:00+0900"),
                ],
            ],
            [
                DateTimeRange(datetime(2015, 3, 23, 0, 0, 0), datetime(2015, 3, 22, 0, 0, 0)),
                relativedelta(hours=-6),
                [
                    datetime(2015, 3, 23, 0, 0, 0),
                    datetime(2015, 3, 22, 18, 0, 0),
                    datetime(2015, 3, 22, 12, 0, 0),
                    datetime(2015, 3, 22, 6, 0, 0),
                    datetime(2015, 3, 22, 0, 0, 0),
                ],
            ],
            [
                DateTimeRange(date(2015, 3, 23), date(2015, 3, 26)),
                relativedelta(days=+1),
                [
                    datetime(2015, 3, 23, 0, 0, 0),
                    datetime(2015, 3, 24, 0, 0, 0),
                    datetime(2015, 3, 25, 0, 0, 0),
                    datetime(2015, 3, 26, 0, 0, 0),
                ],
            ],
        ],
    )
    def test_normal(self, value, step, expected):
        for value_item, expected_item in zip(value.range(step), expected):
            assert value_item == expected_item

    @pytest.mark.parametrize(
        ["value", "step", "expected"],
        [
            [
                DateTimeRange(datetime(2015, 3, 22, 0, 0, 0), datetime(2015, 3, 22, 0, 1, 0)),
                relativedelta(seconds=-60),
                ValueError,
            ],
            [
                DateTimeRange(datetime(2015, 3, 22, 0, 1, 0), datetime(2015, 3, 22, 0, 0, 0)),
                relativedelta(seconds=+60),
                ValueError,
            ],
            [
                DateTimeRange(datetime(2015, 3, 22, 0, 0, 0), datetime(2015, 3, 22, 0, 1, 0)),
                None,
                AttributeError,
            ],
            [
                DateTimeRange(datetime(2015, 3, 22, 0, 0, 0), datetime(2015, 3, 22, 0, 1, 0)),
                1,
                AttributeError,
            ],
            [
                DateTimeRange(datetime(2015, 3, 22, 0, 0, 0), datetime(2015, 3, 22, 0, 1, 0)),
                timedelta(seconds=0),
                ValueError,
            ],
            [
                DateTimeRange(datetime(2015, 3, 22, 0, 0, 0), datetime(2015, 3, 22, 0, 1, 0)),
                relativedelta(months=+0),
                ValueError,
            ],
            [None, relativedelta(months=+4), AttributeError],
            [10, relativedelta(months=+4), AttributeError],
        ],
    )
    def test_exception(self, value, step, expected):
        with pytest.raises(expected):
            for i in value.range(step):
                pass


class Test_DateTimeRange_is_intersection(object):
    @pytest.mark.parametrize(
        ["lhs", "rhs", "expected"],
        [
            [
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
                True,
            ],
            [
                DateTimeRange("2015-01-22T09:50:00+0900", "2015-01-22T10:00:00+0900"),
                DateTimeRange("2015-01-22T10:10:00+0900", "2015-03-22T10:20:00+0900"),
                False,
            ],
            [
                DateTimeRange("2015-01-22T09:50:00", "2015-01-22T10:00:00"),
                DateTimeRange("2015-01-22T10:10:00", "2015-03-22T10:20:00"),
                False,
            ],
            [
                DateTimeRange("2015-01-22T09:50:00+0900", "2015-01-22T10:00:00+0900"),
                DateTimeRange("2015-01-22T10:00:00+0900", "2015-03-22T10:20:00+0900"),
                True,
            ],
            [
                DateTimeRange("2015-01-22T09:50:00+0900", "2015-01-22T10:05:00+0900"),
                DateTimeRange("2015-01-22T10:00:00+0900", "2015-03-22T10:20:00+0900"),
                True,
            ],
            [
                DateTimeRange("2015-01-22T10:00:00+0900", "2015-03-22T10:20:00+0900"),
                DateTimeRange("2015-01-22T09:50:00+0900", "2015-01-22T10:05:00+0900"),
                True,
            ],
            [
                DateTimeRange("2014-01-22T10:00:00 JST", "2016-03-22T10:20:00 JST"),
                DateTimeRange("2015-01-22T09:50:00 JST", "2015-01-22T10:05:00 JST"),
                True,
            ],
            [
                DateTimeRange("2015-01-12T10:00:00 JST", "2015-02-22T10:10:00 JST"),
                DateTimeRange("2015-01-22T10:00:00 JST", "2015-03-22T10:10:00 JST"),
                True,
            ],
        ],
    )
    def test_normal(self, lhs, rhs, expected):
        assert lhs.is_intersection(rhs) == expected

    @pytest.mark.parametrize(
        ["lhs", "rhs", "expected"],
        [
            [DateTimeRange(None, None), DateTimeRange(None, None), TypeError],
            [
                DateTimeRange(None, TEST_END_DATETIME),
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
                TypeError,
            ],
            [
                DateTimeRange(TEST_END_DATETIME, TEST_START_DATETIME),
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
                ValueError,
            ],
            [
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
                DateTimeRange(None, TEST_END_DATETIME),
                TypeError,
            ],
            [
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
                DateTimeRange(TEST_END_DATETIME, TEST_START_DATETIME),
                ValueError,
            ],
        ],
    )
    def test_exception(self, lhs, rhs, expected):
        with pytest.raises(expected):
            lhs.is_intersection(rhs)


class Test_DateTimeRange_get_start_time_str(object):
    @pytest.mark.parametrize(
        ["time_format", "expected"],
        [
            [ISO_TIME_FORMAT, START_DATETIME_TEXT],
            ["%Y/%m/%d %H:%M:%S%z", "2015/03/22 10:00:00+0900"],
        ],
    )
    def test_normal(self, datetimerange_normal, time_format, expected):
        datetimerange_normal.start_time_format = time_format
        assert datetimerange_normal.get_start_time_str() == expected

    def test_abnormal_1(self, datetimerange_null):
        assert datetimerange_null.get_start_time_str() == DateTimeRange.NOT_A_TIME_STR

    def test_abnormal_2(self, datetimerange_normal):
        datetimerange_normal.start_time_format = "aaa"
        assert datetimerange_normal.get_start_time_str() == "aaa"

    @pytest.mark.parametrize(["time_format", "expected"], [[None, TypeError]])
    def test_exception(self, datetimerange_normal, time_format, expected):
        datetimerange_normal.start_time_format = time_format
        with pytest.raises(expected):
            datetimerange_normal.get_start_time_str()


class Test_DateTimeRange_get_end_time_str(object):
    @pytest.mark.parametrize(
        ["time_format", "expected"],
        [[ISO_TIME_FORMAT, END_DATETIME_TEXT], ["%Y/%m/%d %H:%M:%S%z", "2015/03/22 10:10:00+0900"]],
    )
    def test_normal(self, datetimerange_normal, time_format, expected):
        datetimerange_normal.end_time_format = time_format
        assert datetimerange_normal.get_end_time_str() == expected

    def test_abnormal_1(self, datetimerange_null):
        assert datetimerange_null.get_end_time_str() == DateTimeRange.NOT_A_TIME_STR

    def test_abnormal_2(self, datetimerange_normal):
        datetimerange_normal.end_time_format = "aaa"
        assert datetimerange_normal.get_end_time_str() == "aaa"

    @pytest.mark.parametrize(["time_format", "expected"], [[None, TypeError]])
    def test_exception(self, datetimerange_normal, time_format, expected):
        datetimerange_normal.end_time_format = time_format
        with pytest.raises(expected):
            datetimerange_normal.get_end_time_str()


class Test_DateTimeRange_get_timedelta_second(object):
    def test_normal(self, datetimerange_normal):
        assert datetimerange_normal.get_timedelta_second() == 600

    def test_inversion(self, datetimerange_inversion):
        assert datetimerange_inversion.get_timedelta_second() == -600

    def test_null(self, datetimerange_null):
        with pytest.raises(TypeError):
            datetimerange_null.get_timedelta_second()

    def test_exception(self, datetimerange_null_start):
        with pytest.raises(TypeError):
            datetimerange_null_start.get_timedelta_second()


class Test_DateTimeRange_set_start_datetime(object):
    @pytest.mark.parametrize(
        ["value", "timezone", "expected"],
        [
            [START_DATETIME_TEXT, None, TEST_START_DATETIME],
            [TEST_START_DATETIME, None, TEST_START_DATETIME],
            [1485685623, pytz.utc, pytz.utc.localize(datetime(2017, 1, 29, 10, 27, 3))],
            ["1485685623", pytz.utc, pytz.utc.localize(datetime(2017, 1, 29, 10, 27, 3))],
            [
                1485685623,
                pytz.timezone("Asia/Tokyo"),
                pytz.timezone("Asia/Tokyo").localize(datetime(2017, 1, 29, 19, 27, 3)),
            ],
            [None, None, None],
        ],
    )
    def test_normal(self, value, timezone, expected):
        dtr = DateTimeRange(TEST_END_DATETIME, TEST_END_DATETIME)
        dtr.set_start_datetime(value, timezone=timezone)

        assert dtr.start_datetime == expected

    @pytest.mark.parametrize(
        ["value", "expected"], [["invalid time string", ValueError], ["3.3.5", ValueError]]
    )
    def test_null_start(self, datetimerange_null_start, value, expected):
        with pytest.raises(expected):
            datetimerange_null_start.set_start_datetime(value)


class Test_DateTimeRange_set_end_datetime(object):
    @pytest.mark.parametrize(
        ["value", "timezone", "expected"],
        [
            [START_DATETIME_TEXT, None, TEST_START_DATETIME],
            [TEST_START_DATETIME, None, TEST_START_DATETIME],
            [1485685623, pytz.utc, pytz.utc.localize(datetime(2017, 1, 29, 10, 27, 3))],
            ["1485685623", pytz.utc, pytz.utc.localize(datetime(2017, 1, 29, 10, 27, 3))],
            [
                1485685623,
                pytz.timezone("Asia/Tokyo"),
                pytz.timezone("Asia/Tokyo").localize(datetime(2017, 1, 29, 19, 27, 3)),
            ],
            [None, None, None],
        ],
    )
    def test_normal(self, value, timezone, expected):
        dtr = DateTimeRange(TEST_END_DATETIME, TEST_END_DATETIME)
        dtr.set_end_datetime(value, timezone=timezone)

        assert dtr.end_datetime == expected

    @pytest.mark.parametrize(
        ["value", "expected"], [["invalid time string", ValueError], ["3.3.5", ValueError]]
    )
    def test_null_start(self, datetimerange_null_start, value, expected):
        with pytest.raises(expected):
            datetimerange_null_start.set_end_datetime(value)


class Test_DateTimeRange_set_time_range(object):
    @pytest.mark.parametrize(
        ["start", "end", "expected"],
        [
            [
                START_DATETIME_TEXT,
                END_DATETIME_TEXT,
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
            ],
            [None, None, DateTimeRange(None, None)],
        ],
    )
    def test_normal(self, start, end, expected):
        dtr = DateTimeRange()
        dtr.set_time_range(start, end)
        assert dtr == expected

    @pytest.mark.parametrize(
        ["start", "end", "expected"],
        [
            ["invalid time string", END_DATETIME_TEXT, ValueError],
            [START_DATETIME_TEXT, "invalid time string", ValueError],
            ["invalid time string", "invalid time string", ValueError],
        ],
    )
    def test_exception(self, start, end, expected):
        dtr = DateTimeRange()
        with pytest.raises(expected):
            dtr.set_time_range(start, end)


class Test_DateTimeRange_intersection(object):
    @pytest.mark.parametrize(
        ["lhs", "rhs", "expected"],
        [
            [
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
            ],
            [
                DateTimeRange("2015-01-22T09:50:00 JST", "2015-01-22T10:00:00 JST"),
                DateTimeRange("2015-01-22T10:10:00 JST", "2015-03-22T10:20:00 JST"),
                DateTimeRange(None, None),
            ],
            [
                DateTimeRange("2015-01-22T09:50:00 JST", "2015-01-22T10:00:00 JST"),
                DateTimeRange("2015-01-22T10:00:00 JST", "2015-03-22T10:20:00 JST"),
                DateTimeRange("2015-01-22T10:00:00 JST", "2015-01-22T10:00:00 JST"),
            ],
            [
                DateTimeRange("2015-01-22T09:50:00 JST", "2015-01-22T10:05:00 JST"),
                DateTimeRange("2015-01-22T10:00:00 JST", "2015-03-22T10:20:00 JST"),
                DateTimeRange("2015-01-22T10:00:00 JST", "2015-01-22T10:05:00 JST"),
            ],
            [
                DateTimeRange("2015-01-22T10:00:00 JST", "2015-03-22T10:20:00 JST"),
                DateTimeRange("2015-01-22T09:50:00 JST", "2015-01-22T10:05:00 JST"),
                DateTimeRange("2015-01-22T10:00:00 JST", "2015-01-22T10:05:00 JST"),
            ],
            [
                DateTimeRange("2014-01-22T10:00:00 JST", "2016-03-22T10:20:00 JST"),
                DateTimeRange("2015-01-22T09:50:00 JST", "2015-01-22T10:05:00 JST"),
                DateTimeRange("2015-01-22T09:50:00 JST", "2015-01-22T10:05:00 JST"),
            ],
            [
                DateTimeRange("2015-01-12T10:00:00 JST", "2015-02-22T10:10:00 JST"),
                DateTimeRange("2015-01-22T10:00:00 JST", "2015-03-22T10:10:00 JST"),
                DateTimeRange("2015-01-22T10:00:00 JST", "2015-02-22T10:10:00 JST"),
            ],
        ],
    )
    def test_normal(self, lhs, rhs, expected):
        lhs_org = deepcopy(lhs)

        assert lhs.intersection(rhs) == expected
        assert lhs == lhs_org

    @pytest.mark.parametrize(
        ["lhs", "rhs", "expected"],
        [
            [DateTimeRange(None, None), DateTimeRange(None, None), TypeError],
            [
                DateTimeRange(None, TEST_END_DATETIME),
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
                TypeError,
            ],
            [
                DateTimeRange(TEST_END_DATETIME, TEST_START_DATETIME),
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
                ValueError,
            ],
            [
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
                DateTimeRange(None, TEST_END_DATETIME),
                TypeError,
            ],
            [
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
                DateTimeRange(TEST_END_DATETIME, TEST_START_DATETIME),
                ValueError,
            ],
        ],
    )
    def test_exception(self, lhs, rhs, expected):
        with pytest.raises(expected):
            lhs.intersection(rhs)


class Test_DateTimeRange_encompass(object):
    @pytest.mark.parametrize(
        ["lhs", "rhs", "expected"],
        [
            [
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
            ],
            [
                DateTimeRange("2015-01-22T09:50:00 JST", "2015-01-22T10:00:00 JST"),
                DateTimeRange("2015-01-22T10:10:00 JST", "2015-01-22T10:20:00 JST"),
                DateTimeRange("2015-01-22T09:50:00 JST", "2015-01-22T10:20:00 JST"),
            ],
            [
                DateTimeRange("2015-01-22T09:50:00 JST", "2015-01-22T10:00:00 JST"),
                DateTimeRange("2015-01-22T10:00:00 JST", "2015-01-22T10:20:00 JST"),
                DateTimeRange("2015-01-22T09:50:00 JST", "2015-01-22T10:20:00 JST"),
            ],
            [
                DateTimeRange("2015-01-22T09:50:00 JST", "2015-01-22T10:05:00 JST"),
                DateTimeRange("2015-01-22T10:00:00 JST", "2015-01-22T10:20:00 JST"),
                DateTimeRange("2015-01-22T09:50:00 JST", "2015-01-22T10:20:00 JST"),
            ],
            [
                DateTimeRange("2015-01-22T10:00:00 JST", "2015-03-22T10:20:00 JST"),
                DateTimeRange("2015-01-22T09:50:00 JST", "2015-01-22T10:05:00 JST"),
                DateTimeRange("2015-01-22T09:50:00 JST", "2015-03-22T10:20:00 JST"),
            ],
        ],
    )
    def test_normal(self, lhs, rhs, expected):
        lhs_org = deepcopy(lhs)

        assert lhs.encompass(rhs) == expected
        assert lhs == lhs_org

    @pytest.mark.parametrize(
        ["lhs", "rhs", "expected"],
        [
            [DateTimeRange(None, None), DateTimeRange(None, None), TypeError],
            [
                DateTimeRange(None, TEST_END_DATETIME),
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
                TypeError,
            ],
            [
                DateTimeRange(TEST_END_DATETIME, TEST_START_DATETIME),
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
                ValueError,
            ],
            [
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
                DateTimeRange(None, TEST_END_DATETIME),
                TypeError,
            ],
            [
                DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME),
                DateTimeRange(TEST_END_DATETIME, TEST_START_DATETIME),
                ValueError,
            ],
        ],
    )
    def test_exception(self, lhs, rhs, expected):
        with pytest.raises(expected):
            lhs.encompass(rhs)


class Test_DateTimeRange_truncate(object):
    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            [0, DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME)],
            [10, DateTimeRange("2015-03-22 10:00:30" + TIMEZONE, "2015-03-22 10:09:30" + TIMEZONE)],
        ],
    )
    def test_normal(self, datetimerange_normal, value, expected):
        datetimerange_normal.truncate(value)
        assert datetimerange_normal == expected

    @pytest.mark.parametrize(["value", "expected"], [[-10, ValueError]])
    def test_exception(self, datetimerange_normal, value, expected):
        with pytest.raises(expected):
            datetimerange_normal.truncate(value)

    @pytest.mark.parametrize(["value"], [[10]])
    def test_null(self, datetimerange_null_start, value):
        with pytest.raises(TypeError):
            datetimerange_null_start.truncate(value)
