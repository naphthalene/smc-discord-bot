#!/usr/bin/env python3

import os
import discord

from smc import SMC

client = discord.Client()
current_smc = None

def check_smc():
    """
    Reset current_smc to None if it is over
    """
    global current_smc
    if current_smc is not None:
        if not current_smc.ongoing():
            current_smc = None

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    """
    Main handler for messages
    """
    async def delegate_cmd(smc, command, msg):
        """
        Executes the appropriate coro on the smc class
        """
        await {
            'in'        : smc.join,
            'start'     : smc.start,
            'cancel'    : smc.cancel,
            'join'      : smc.join,
            'info'      : smc.info,
            'submit'    : smc.submit,
        }[command](msg)

    async def parse_cmd():
        """
        Parse the message for a command.
        Ensure its not a message from the bot and that its preceded by a bang
        """
        if not message.content.startswith('!') or message.author == client.user:
            return

        global current_smc
        check_smc()
        try:
            command_name, duration, *topic = message.content.split()
            command_name = command_name.replace('!', '').strip()
        if command_name == 'smc':
            if current_smc is not None and current_smc.ongoing():
                await message.channel.send(f"~ error: Cannot start an SMC while another is ongoing ~")
                return
            valid, validate_msg = SMC.validate_command(parts)
            if not valid:
                await message.channel.send(f"~ error: {validate_msg} ~")
                await message.channel.send(SMC._help)
            else:
                current_smc = SMC(
                    owner=message.author,
                    channel=message.channel,
                    topic=' '.join(parts[2:]),
                    duration=int(parts[1])
                )
                await current_smc._announce()
        else:
            # Delegate to the SMC class
            if current_smc is None:
                await message.channel.send('~ error: No currently running SMC ~')
            else:
                await delegate_cmd(current_smc, command_name, message)

    await parse_cmd()

client.run(os.environ['DISCORD_TOKEN'])
