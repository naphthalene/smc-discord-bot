from timer import Timer

class SMC:
    """
    A challenge itself
    """
    _help = """```
    !smc <challenge-duration> <TOPIC>   ; Define a challenge
    !info                               ; Challenge info
    !in                                 ; Join the challenge
    !start                              ; Start the challenge
    !cancel                             ; Cancel the challenge
    !submit <LINK>                      ; Submit your entry
    ```
    """
    def __init__(self, *, owner, channel, topic, duration):
        self.owner = owner
        self.channel = channel
        self.duration = duration * 60
        self.topic = topic
        self.members = set()
        self.entries = {}
        self.state = 'CREATED'
        self.timer = None

    @staticmethod
    def format_user(user):
        return f"{user.name}#{user.discriminator}"

    def __repr__(self):
        msg = (f"Topic: {self.topic}\n"
               f"Contestants: {self.members}\n"
               f"Duration: {(self.duration / 60):.2f} minutes"
        if self.timer is not None:
            msg += f"\nRemaining: {(self.timer.remaining / 60):.2f} minutes"
        return msg

    async def _announce(self):
        """
        Announce the start of challenge
        """
        await self.channel.send('~ Starting SMC ~')
        await self.channel.send(repr(self))
        await self.channel.send('~ Join with `!in` ~')

    @staticmethod
    def validate_command(parts):
        if len(parts) < 3:
            return (False, 'Not enough args')
        if int(parts[1]) <= 0:
            return (False, 'Challenge time cannot be zero or negative')
        return (True, None)

    def is_owner(self, author):
        """
        Whether this message author is the owner
        """
        return self.owner == author

    async def join(self, msg) -> None:
        """
        A user joins the challenge
        """
        user = self.format_user(msg.author)
        if self.state in ['STARTED']:
            await self.channel.send('~ error: Sorry, this SMC has already begun ~')
        elif self in self.members:
            await self.channel.send(f"~ {user} is already competing ~")
        else:
            await self.channel.send(f"~ {user} has joined! ~")
            self.members.add(user)

    async def leave(self, msg) -> None:
        """
        A user leaves the challenge before it ends
        """
        if not self.ongoing():
            await self.channel.send('~ error: This SMC already ended ~')
            return
        user = self.format_user(msg.author)
        if user in self.members:
            await self.channel.send(f"~ {user} has left the challenge ~")
            self.members.remove(user)
        else:
            await self.channel.send(f"~ error: {user} is not participating ~")

    async def start(self, msg) -> None:
        """
        Start the SMC
        """
        if not self.is_owner(msg.author):
            await self.channel.send(f"~ error: Only {msg.author} can start this SMC ~")
            return
        if len(self.members) == 0:
            await self.channel.send(f"~ error: Nobody is competing! ~")
            return
        await self.channel.send(f"~ SMC IS STARTING ~")
        self.state = 'STARTED'
        self.timer = Timer(self.duration, self._challenge_elapsed)

    async def cancel(self, msg) -> None:
        """
        Cancel the SMC
        """
        if not self.is_owner(msg.author):
            await self.channel.send(f"~ error: Only {self.owner} can cancel this SMC ~")
            return
        if self.ongoing() and self.timer is not None:
            await self.channel.send(f"~ SMC is CANCELLED! ~")
            self.state = 'CANCELLED'
            self.timer.cancel()

    async def submit(self, msg) -> None:
        """
        Submit an entry
        """
        formatted_user = self.format_user(msg.author)
        link = msg.content.split()[1:]
        if formatted_user not in self.members:
            await self.channel.send(f"~ {formatted_user} is not participating in this SMC ~")
            return

        if formatted_user in self.entries.keys():
            await self.channel.send(f"~ {formatted_user} re-submitted with {link} ! ~")
        else:
            await self.channel.send(f"~ {formatted_user} submitted {link} ! ~")
        self.entries[formatted_user] = link

    async def info(self, _) -> None:
        """
        Print SMC info
        """
        await self.channel.send(repr(self))

    def ongoing(self) -> bool:
        """
        Is the SMC active?
        """
        return self.state in ['CREATED', 'STARTED']

    async def _challenge_elapsed(self):
        """
        The join period is over, all members have joined
        """
        await self.channel.send(f"~ SMC is _OVER_ ~")
        await self.channel.send(f"~ Entries: {self.entries} ~")
        self.state = 'COMPLETED'
