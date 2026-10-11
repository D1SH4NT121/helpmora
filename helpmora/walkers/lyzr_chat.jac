"""LyzrChatWalker — Direct inference with deployed Lyzr Agent Studio."""

walker LyzrChatWalker {
    has message: str;
    has user_id: str = "futurexprime21@gmail.com";
    has session_id: str = "";

    can chat with `Root entry {
        import from integrations.lyzr.chat { query_lyzr_agent }
        res = query_lyzr_agent(
            message=self.message,
            user_id=self.user_id,
            session_id=self.session_id
        );
        report res;
    }
}
