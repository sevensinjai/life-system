/** The quote collection and the one line a day it surfaces. */

import {
  delegate,
  empty,
  esc,
  fmtDate,
  fmtDateTime,
  formValues,
  plural,
  qs,
  toast,
} from "../dom.js";

const BULK_SEPARATOR = " -- ";

/** Parse the bulk textarea: one quote per line, optional " -- author" suffix. */
export function parseBulk(text) {
  return text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const at = line.lastIndexOf(BULK_SEPARATOR);
      if (at === -1) return { text: line };
      return {
        text: line.slice(0, at).trim(),
        author: line.slice(at + BULK_SEPARATOR.length).trim() || null,
      };
    })
    .filter((quote) => quote.text);
}

function todayCard(daily) {
  const quote = daily.quote;
  return `
    <div class="card">
      <div class="spread">
        <h2>Today's quote</h2>
        <span class="pill">${fmtDate(daily.local_date)}</span>
      </div>
      ${
        quote
          ? `<blockquote style="margin:0.6rem 0;font-size:1.15rem;line-height:1.5">
               &ldquo;${esc(quote.text)}&rdquo;
             </blockquote>
             <p class="muted">${quote.author ? `— ${esc(quote.author)}` : "— you"}
             &middot; <span class="mono">#${quote.id}</span></p>`
          : empty("Nothing in rotation yet. Write one below.")
      }
      <p class="muted mono" style="margin-bottom:0;font-size:0.78rem">
        pool ${daily.pool_size} &middot; turns over ${fmtDateTime(daily.refresh_after)}
      </p>
    </div>`;
}

function quoteItem(quote) {
  return `
    <article class="item${quote.is_active ? "" : " archived"}">
      <div class="spread">
        <div>
          <p style="margin:0">&ldquo;${esc(quote.text)}&rdquo;</p>
          <p class="muted mono" style="margin:0.25rem 0 0;font-size:0.76rem">
            #${quote.id}${quote.author ? ` &middot; ${esc(quote.author)}` : ""}
            ${quote.is_active ? "" : "&middot; retired"}
          </p>
        </div>
        <div class="row">
          <button class="btn small ghost" data-action="edit-quote" data-id="${quote.id}" type="button">Edit</button>
          ${
            quote.is_active
              ? `<button class="btn small danger" data-action="retire" data-id="${quote.id}" type="button">Retire</button>`
              : `<button class="btn small ghost" data-action="restore-quote" data-id="${quote.id}" type="button">Restore</button>`
          }
        </div>
      </div>
    </article>`;
}

export function createQuotesView(ctx) {
  const root = qs("#view-quotes");
  const dialog = document.createElement("dialog");
  document.body.append(dialog);
  let includeArchived = false;

  async function refresh() {
    const [daily, quotes] = await Promise.all([
      ctx.api.quoteOfTheDay(),
      ctx.api.quotes({ include_archived: includeArchived ? "true" : undefined }),
    ]);

    root.innerHTML = `
      <div class="grid">
        <div>
          ${todayCard(daily)}
          <div class="card">
            <h2>Write a quote</h2>
            <form id="create-quote" class="stack">
              <label class="field">
                <span>Text</span>
                <input name="text" type="text" maxlength="500" required placeholder="Arise." />
              </label>
              <label class="field">
                <span>Author</span>
                <input name="author" type="text" maxlength="120" placeholder="leave blank for your own" />
              </label>
              <div class="row"><button class="btn primary" type="submit">Add</button></div>
            </form>
          </div>
          <div class="card">
            <h2>Paste a batch</h2>
            <form id="bulk-quotes" class="stack">
              <label class="field">
                <span>One per line, optionally <code>text -- author</code></span>
                <textarea name="bulk" placeholder="Arise. -- The System&#10;Hard days make hard people.&#10;One more rep."></textarea>
                <small>Duplicates already in rotation are skipped, not rejected.</small>
              </label>
              <div class="row"><button class="btn" type="submit">Add batch</button></div>
            </form>
          </div>
        </div>

        <div class="card">
          <div class="spread">
            <h2>Collection</h2>
            <span class="pill">${plural(quotes.length, "quote")}</span>
          </div>
          <label class="checkbox" style="margin:0.4rem 0 0.8rem">
            <input type="checkbox" data-filter="include_archived"${
              includeArchived ? " checked" : ""
            } /> include retired
          </label>
          ${
            quotes.length
              ? quotes.map(quoteItem).join("")
              : empty("No quotes yet. The lock screen has nothing to show.")
          }
        </div>
      </div>`;
  }

  async function openEditor(id) {
    const quote = await ctx.api.quote(id);
    dialog.innerHTML = `
      <form method="dialog" data-quote-id="${quote.id}">
        <h2>Edit quote #${quote.id}</h2>
        <div class="stack">
          <label class="field">
            <span>Text</span>
            <input name="text" type="text" maxlength="500" required value="${esc(
              quote.text
            )}" />
          </label>
          <label class="field">
            <span>Author</span>
            <input name="author" type="text" maxlength="120" value="${esc(
              quote.author ?? ""
            )}" />
          </label>
          <label class="checkbox">
            <input type="checkbox" name="is_active"${
              quote.is_active ? " checked" : ""
            } /> in rotation
          </label>
        </div>
        <div class="row" style="margin-top:0.9rem">
          <button class="btn primary" type="submit">Save</button>
          <button class="btn ghost" type="button" data-action="cancel">Cancel</button>
        </div>
      </form>`;
    dialog.showModal();
  }

  dialog.addEventListener("click", (event) => {
    if (event.target.dataset.action === "cancel") dialog.close();
  });

  dialog.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.target;
    const values = formValues(form);
    await ctx.guard(async () => {
      await ctx.api.updateQuote(Number(form.dataset.quoteId), {
        text: values.text,
        author: values.author ?? null,
        is_active: form.querySelector("[name='is_active']").checked,
      });
      dialog.close();
      toast("Quote updated.", "success");
      await ctx.refresh("quotes");
    });
  });

  delegate(root, "click", "[data-action]", async (event, button) => {
    const id = Number(button.dataset.id);
    await ctx.guard(async () => {
      switch (button.dataset.action) {
        case "edit-quote":
          await openEditor(id);
          return;
        case "retire":
          await ctx.api.archiveQuote(id);
          toast("Quote retired. It keeps its id.");
          break;
        case "restore-quote":
          await ctx.api.updateQuote(id, { is_active: true });
          toast("Quote back in rotation.", "success");
          break;
        default:
          return;
      }
      await ctx.refresh("quotes");
    });
  });

  root.addEventListener("change", async (event) => {
    if (event.target.dataset.filter !== "include_archived") return;
    includeArchived = event.target.checked;
    await ctx.guard(refresh);
  });

  root.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.target;

    if (form.id === "create-quote") {
      const values = formValues(form);
      await ctx.guard(async () => {
        await ctx.api.createQuote({ text: values.text, author: values.author ?? null });
        form.reset();
        toast("Quote added to the rotation.", "success");
        await ctx.refresh("quotes");
      });
      return;
    }

    if (form.id === "bulk-quotes") {
      const drafts = parseBulk(form.querySelector("textarea").value);
      if (!drafts.length) {
        toast("Nothing to add — write one quote per line.", "error");
        return;
      }
      await ctx.guard(async () => {
        const result = await ctx.api.createQuotes(drafts);
        form.reset();
        toast(
          `Added ${result.created_count}` +
            (result.skipped_count ? `, skipped ${result.skipped_count} duplicate.` : "."),
          "success"
        );
        await ctx.refresh("quotes");
      });
    }
  });

  return { refresh, clear: () => (root.innerHTML = "") };
}
