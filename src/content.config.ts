import { defineCollection } from "astro:content";
import { docsLoader } from "@astrojs/starlight/loaders";
import { docsSchema } from "@astrojs/starlight/schema";
import { z } from "astro/zod";
import { blogSchema } from "starlight-blog/schema";
import { topicSchema } from "starlight-sidebar-topics/schema";

export const collections = {
    docs: defineCollection({
        loader: docsLoader(),
        schema: docsSchema({
            extend: (context) =>
                blogSchema(context).extend({
                    ...topicSchema.shape,
                    giscus: z.boolean().optional().default(true),
                }),
        }),
    }),
};
