#!/usr/bin/env python
import hashlib


class VatHasher(object):
	"""Vat Hasher takes the server challenge packet in the constructor"""

	version = 8464
	#vstars's private keys
	PRIVATE_SALT = "945507c4c50222c34687e742729252e6"

	def __init__(self, serverChallenge):
		super(VatHasher, self).__init__()
		self.serverSalt = self.lastSalt = self.computeHash(serverChallenge, self.version, self.PRIVATE_SALT)
			
	def computeHash(self,challenge, version, salt):
		saltFirst = salt[:12]
		saltLast = salt[12:-10]
		saltMiddle = salt[0x16:32]


		challengeFirst  = challenge[:len(challenge)/2]
		challengeSecond = challenge[len(challenge)/2:]

		if (version % 2) != 0:
			first = challengeSecond
			second = challengeFirst
		else:
			first = challengeFirst
			second = challengeSecond

		formatMod = version % 3
		response = ""
		if formatMod == 0:
			response = "%s%s%s%s%s" % (saltFirst, first,saltLast,second,saltMiddle)
		elif formatMod == 1:
			response = "%s%s%s%s%s" % (saltLast, first,saltMiddle,second,saltFirst)
		else:
			response = "%s%s%s%s%s" % (saltMiddle, first,saltFirst,second,saltLast)
		return hashlib.md5(response).hexdigest()


	def hash(self,challenge):
		computedhash = self.computeHash(challenge,self.version,self.lastSalt)
		#print computedhash

		catHash= "%s%s" %(self.serverSalt,computedhash)
		#print "CATHASH: %s" % (catedHash)

		self.lastSalt = hashlib.md5(catHash).hexdigest()
		return computedhash

def main():
	vathash = VatHasher("8750e0f43a0633")
	print vathash.serverSalt
	print vathash.hash("10b08558f1")


if __name__ == '__main__':
	main()



