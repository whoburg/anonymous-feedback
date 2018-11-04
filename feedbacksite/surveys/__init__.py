from os.path import expanduser
import gnupg
gpg = gnupg.GPG(gnupghome=expanduser('~/.gnupg/'))
