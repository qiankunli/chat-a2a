#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from app.model.conversation_po import ConversationModel
from pkg.acrud_plus.crud import ACRUDPlus


class CRUDConversation(ACRUDPlus[ConversationModel]):
    def __init__(self):
        super().__init__(ConversationModel)
