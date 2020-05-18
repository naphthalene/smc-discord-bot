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
        Execute the appropriate
        """
        if not message.content.startswith('!'):
            return

        global current_smc
        check_smc()
        parts = message.content.split()
        command_name = parts[0].replace('!', '')
        if command_name == 'smc':
            if current_smc is not None and current_smc.ongoing():
                await message.channel.send(f"~ error: Cannot start another SMC while another is ongoing ~")
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

    # Ignore messages from self
    if message.author == client.user:
        return

    await parse_cmd()

client.run(os.environ['DISCORD_TOKEN'])
