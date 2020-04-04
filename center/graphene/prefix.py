class Prefix:
    """ This class is meant to allow changing the prefix.
        The prefix is used to link a public key to a specific blockchain.
    """

    prefix = "EOS"

    def set_prefix(self, prefix):
        if prefix:
            self.prefix = prefix