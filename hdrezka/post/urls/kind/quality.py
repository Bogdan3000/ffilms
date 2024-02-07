"""high-level representation of video quality"""
from .._regexes import match_quality_int, match_quality_int_k

__all__ = ('Quality',)


class Quality(str):
    """str type add-on to represent video quality"""
    __slots__ = ('_i', 'addon')
    addon: str

    def __init__(self, *_, **__):
        """Sets addon attribute (can contain 'ultra')"""
        _match = match_quality_int(self)
        _k_match = match_quality_int_k(self)
        if not _match and not _k_match:
            raise ValueError(f'{self!r} is not quality.')

        if _match:
            _i, self.addon = _match.groups()
            self._i = int(_i)
        else:
            _i, self.addon = _k_match.groups()
            self._i = _i  # Оставляем _i как строку

    def __int__(self):
        """
        returns pixels height
        """
        return self._i

    def __lt__(self, other):
        """Is other quality better than self"""
        if not isinstance(other, self.__class__):
            return super().__le__(other)
        if not (self.addon or other.addon):
            return int(self._i) < int(other._i)
        return False
